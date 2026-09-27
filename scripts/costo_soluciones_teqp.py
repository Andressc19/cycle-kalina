"""Costo en segundos de las soluciones al estado espurio de teqp — tarea
2026-09-27-costo-soluciones-teqp. Mide el costo de (A) "teqp verificado" (una
llamada al motor real SOLO cuando la T invertida cae en la zona de riesgo) y de
(B) verificacion final de la salida isentropica de turbina contra el motor real,
ANTES de elegir entre ellas. El motor NO se modifica; este script solo escribe en
`resultados/2026-09-27_costo_soluciones/`. Que hace cada parte, punto por punto,
esta en REPORTE_COSTO_SOLUCIONES.md. Zona de riesgo: x_molar>=0.9 y
|T-Ta(P)|<1 K, o x_molar<=0.1 y |T-Tw(P)|<1 K, con Ta,Tw = `ng.Tsat_pure(P_pa)`.
Uso: `python -u` (las 4 partes) o `python -u 4` (solo la tabla, desde los CSV).
"""
from __future__ import annotations

import csv
import statistics as st
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))

from src.cycle_solver import resolver_ciclo  # noqa: E402
from src.properties import _teqp_engine as ng  # noqa: E402
from src.properties.adapter import PropertyRangeError  # noqa: E402
from src.properties.ammonia_water_adapter import AmmoniaWaterAdapter  # noqa: E402
from src.properties.teqp_adapter import TeqpAdapter  # noqa: E402

OUT = REPO / "resultados" / "2026-09-27_costo_soluciones"
SRC_MARGEN = REPO / "resultados" / "2026-09-24_margen2k" / "barrido_margen2k.csv"
SRC_VERIF = REPO / "resultados" / "2026-09-24_verificacion" / "verificacion_motor_real.csv"
EPS = (0.85, 0.80, 0.85)                    # efectividades fijas del TASK
T_SUMIDERO, ETA_T, ETA_P, M_B = 283.0, 0.80, 0.80, 1.0
ZONA_T, X_ALTO, X_BAJO = 1.0, 0.90, 0.10     # criterio de zona de riesgo [K]
METODOS = ("h_T", "h_s", "s", "T_from_Ph", "T_from_Ps", "bubble_point",
           "dew_point", "equilibrio_liquido_vapor", "fase_de")
METODOS_REAL = ("h(P,s,x)", "T_from_Ps", "T_from_Ph")
EXC = (PropertyRangeError, ValueError, RuntimeError, NotImplementedError)
PUNTOS_3 = [("NORMAL-1", 0.65, 5000.0, 423.0, 704.644595), ("NORMAL-2", 0.80, 5000.0, 394.0, 952.892781),
            ("NORMAL-3", 0.60, 3000.0, 394.0, 523.749936), ("ESPURIA", 0.60, 4000.0, 394.0, 423.914831),
            ("FISICA", 0.60, 4000.0, 394.0, 424.169832)]


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def escribir(nombre, filas):
    if not filas:
        return
    with open(OUT / nombre, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(filas[0].keys()))
        w.writeheader()
        w.writerows(filas)
    log(f"  -> {nombre} ({len(filas)} filas)")


def en_zona(P_pa, w, T):
    """True si la T de una inversion cae en la franja de riesgo del TASK."""
    Ta, Tw = ng.Tsat_pure(P_pa)
    xm = ng.w2m(w)
    return ((xm >= X_ALTO and abs(T - Ta) < ZONA_T)
            or (xm <= X_BAJO and abs(T - Tw) < ZONA_T))


def _crono(nombre):
    """Reenvia al metodo de la clase base contando llamadas y cronometrando."""
    def deco(fn):
        def env(self, *a, **k):
            # `h` tiene dos modos de entrada, y siempre por palabra clave: T o s
            n = ("h_s" if (k.get("T") is None and k.get("s") is not None)
                 else "h_T") if nombre == "h" else nombre
            self._actual, t0 = n, time.perf_counter()
            try:
                return fn(self, *a, **k)
            finally:
                c = self.cuentas.setdefault(n, [0, 0.0])
                c[0] += 1
                c[1] += time.perf_counter() - t0
        env.__name__ = nombre
        return env
    return deco


class TeqpContado(TeqpAdapter):
    """`TeqpAdapter` que solo cuenta y cronometra: no cambia ningun resultado. La T
    de cada inversion se captura sobreescribiendo `_T_de` (metodo PRIVADO que las
    tres inversiones publicas ya usan): marcar la zona no cuesta ni una segunda
    inversion ni altera un solo digito del resultado."""

    def __init__(self, x=0.5):
        super().__init__(x)
        self.cuentas = {m: [0, 0.0] for m in METODOS}
        self.zonas, self._actual = [], "-"

    def _T_de(self, P_pa, w, *, h=None, s=None):
        T = super()._T_de(P_pa, w, h=h, s=s)
        if en_zona(P_pa, w, T):
            Ta, Tw = ng.Tsat_pure(P_pa)
            self.zonas.append(dict(metodo=self._actual, P=round(P_pa / 1000.0, 6),
                                   x_molar=round(ng.w2m(w), 6), T=round(T, 4),
                                   Ta=round(Ta, 4), Tw=round(Tw, 4)))
        return T


for _n in ("h",) + METODOS[2:]:                 # h se contabiliza como h_T / h_s
    if hasattr(TeqpAdapter, _n):
        setattr(TeqpContado, _n, _crono(_n)(getattr(TeqpAdapter, _n)))


class TeqpVerificado(TeqpAdapter):
    """Opcion A: teqp con respaldo del motor real SOLO en la zona de riesgo. Hace
    la inversion de teqp una sola vez (la T se captura en `_T_de`, sin repetirla);
    si cae en la zona, repite la MISMA llamada con `AmmoniaWaterAdapter` y devuelve
    su resultado. Fuera de la zona devuelve exactamente lo de `TeqpAdapter`.
    """

    def __init__(self, x=0.5):
        super().__init__(x)
        self.real = AmmoniaWaterAdapter(x=x)
        self.recurrencias, self.t_real, self._ultima = [], 0.0, None

    def _T_de(self, P_pa, w, *, h=None, s=None):
        T = super()._T_de(P_pa, w, h=h, s=s)
        self._ultima = (P_pa, w, T)
        return T

    def _respaldo(self, metodo, P, x, v_teqp, repetir):
        """Repite la llamada con el motor real si la T invertida cae en zona."""
        P_pa, w, T = self._ultima or (None, None, None)
        if P_pa is None or not en_zona(P_pa, w, T):
            return v_teqp
        t0, valor, err = time.perf_counter(), None, ""
        try:
            valor = repetir()
        except EXC as exc:      # el motor real no cubre el estado: no se inventa
            err = f"FALLO {type(exc).__name__}: {exc}"[:100]
        self.t_real += time.perf_counter() - t0
        Ta, _ = ng.Tsat_pure(P_pa)
        self.recurrencias.append(dict(metodo=metodo, P=round(P, 6), x=round(w, 6),
                                      x_molar=round(ng.w2m(w), 6), T_teqp=round(T, 4),
                                      Ta=round(Ta, 4), valor_real=valor if valor is not None else err,
                                      t_real_s=round(time.perf_counter() - t0, 3)))
        return v_teqp if valor is None else valor

    def h(self, P, T=None, x=None, s=None, quality=None):
        r = super().h(P, T=T, x=x, s=s, quality=quality)
        if T is None and s is not None:
            r = self._respaldo("h_s", P, x, r, lambda: self.real.h(P, s=s, x=x))
        return r

    def T_from_Ph(self, P, h, x=None):
        return self._respaldo("T_from_Ph", P, x, super().T_from_Ph(P, h, x),
                              lambda: self.real.T_from_Ph(P, h, x))

    def T_from_Ps(self, P, s, x=None):
        return self._respaldo("T_from_Ps", P, x, super().T_from_Ps(P, s, x),
                              lambda: self.real.T_from_Ps(P, s, x))


def ciclo(be, x_b, P_alta, T_fuente, P_baja):
    """Resuelve un ciclo con `be`; devuelve (estado del punto, dt en s)."""
    t0 = time.perf_counter()
    try:
        res = resolver_ciclo(be, P_alta=P_alta, P_baja=P_baja, T_fuente=T_fuente,
                             T_sumidero=T_SUMIDERO, x_b=x_b, m_b=M_B, eta_t=ETA_T,
                             eta_p=ETA_P, eps_hrvg=EPS[0], eps_reg=EPS[1], eps_cond=EPS[2])
        e3, e4 = res["estados"]["e3"], res["estados"]["e4"]
        fila = dict(eta=round(res["eta"], 6), h4=round(e4.h, 4), T4=round(e4.T, 4),
                    s3=round(e3.s, 6), x3=round(e3.x, 6), err="")
    except EXC as exc:
        fila = dict(eta="", h4="", T4="", s3="", x3="", err=f"{type(exc).__name__}: {exc}"[:150])
    return fila, time.perf_counter() - t0


def parte1():
    log("PARTE 1 — instrumentacion: cuantas llamadas caen en la zona de riesgo")
    t0 = time.perf_counter()
    for _ in range(200):
        ng.Tsat_pure(424000.0)
    t_det = (time.perf_counter() - t0) / 200.0
    log(f"  ng.Tsat_pure: {t_det * 1e3:.3f} ms por llamada (media de 200)")
    with open(SRC_MARGEN, newline="", encoding="utf-8") as fh:
        rs = [r for r in csv.DictReader(fh) if r["clasificacion"] == "KALINA"]
    log(f"  {len(rs)} puntos KALINA leidos de {SRC_MARGEN.name}")
    C = ("x_b", "P_alta", "T_fuente", "P_baja")
    puntos = [(f"KALINA-{i + 1:02d}",) + tuple(float(r[k]) for k in C) for i, r in enumerate(rs)]
    filas, tdet, detalle = [], [], []
    for etiq, x_b, P_alta, T_f, P_baja in puntos + PUNTOS_3[3:]:
        be = TeqpContado(x=x_b)
        f, dt = ciclo(be, x_b, P_alta, T_f, P_baja)
        f.update(etiqueta=etiq, x_b=x_b, P_alta=P_alta, T_fuente=T_f, P_baja=P_baja)
        n_inv = sum(be.cuentas[m][0] for m in ("h_s", "T_from_Ph", "T_from_Ps"))
        n_z, n_tot = len(be.zonas), sum(v[0] for v in be.cuentas.values())
        f.update(tiempo_s=round(dt, 2), n_total=n_tot, n_inv=n_inv, n_zona=n_z,
                 pct_zona_inv=100.0 * n_z / n_inv if n_inv else 0.0,
                 pct_zona_tot=100.0 * n_z / max(1, n_tot),
                 overhead_deteccion_s=round(n_inv * t_det, 3),
                 _t=[dict(etiqueta=etiq, metodo=m, n=be.cuentas[m][0],
                          t_s=round(be.cuentas[m][1], 4)) for m in METODOS])
        filas.append(f)
        if f["s3"] != "":
            tdet.append(dict(etiqueta=etiq, P=P_baja, s3=f["s3"], x3=f["x3"], h4=f["h4"]))
        detalle += [dict(etiqueta=etiq, **z) for z in be.zonas]
        log(f"  {etiq} x={x_b} P*={P_baja} eta={f['eta']} t={dt:.1f}s "
            f"llamadas={f['n_total']} inv={n_inv} zona={n_z}")
    escribir("parte1_instrumentacion.csv", [{k: v for k, v in f.items() if k != "_t"} for f in filas])
    escribir("parte1_tiempos_metodo.csv", [r for f in filas for r in f["_t"]])
    escribir("parte1_llamadas_zona.csv", detalle)
    log(f"  TOTAL zona: {sum(f['n_zona'] for f in filas)} llamadas en "
        f"{sum(1 for f in filas if f['n_zona'])}/{len(filas)} puntos")
    return filas, tdet


def parte2(turbinas):
    log("PARTE 2 — costo del motor real por llamada (5 salidas de turbina reales)")
    filas = []
    for t in ([turbinas[min(i, len(turbinas) - 1)] for i in (0, 5, 11, 16, 21)] if turbinas else []):
        be = AmmoniaWaterAdapter(x=t["x3"])
        for metodo, fn, ud in (
                ("h(P,s,x)", lambda b=be, t=t: b.h(t["P"], s=t["s3"], x=t["x3"]), "kJ/kg"),
                ("T_from_Ps", lambda b=be, t=t: b.T_from_Ps(t["P"], t["s3"], t["x3"]), "K"),
                ("T_from_Ph", lambda b=be, t=t: b.T_from_Ph(t["P"], t["h4"], t["x3"]), "K")):
            t0 = time.perf_counter()
            try:
                v, err = round(float(fn()), 6), ""
            except EXC as exc:
                v, err = "", f"{type(exc).__name__}: {exc}"[:120]
            filas.append(dict(etiqueta=t["etiqueta"], metodo=metodo, P=t["P"],
                              s3=round(t["s3"], 6), x3=round(t["x3"], 6),
                              h4=round(t["h4"], 4), valor=v, unidad=ud,
                              tiempo_s=round(time.perf_counter() - t0, 3), error=err))
            log(f"  {t['etiqueta']} {metodo}: {v} {ud} en {filas[-1]['tiempo_s']}s {err}")
    escribir("parte2_costo_motor_real.csv", filas)
    resumen = {}
    for m in METODOS_REAL:
        ts = [f["tiempo_s"] for f in filas if f["metodo"] == m]
        resumen[m] = (st.mean(ts), max(ts))
        log(f"  {m}: media {st.mean(ts):.2f}s  max {max(ts):.2f}s  (n={len(ts)})")
    return resumen


def parte3(filas_p1):
    log("PARTE 3 — prototipo A (TeqpVerificado): 3 KALINA normales + punto del salto")
    ref = {f["etiqueta"]: f["eta"] for f in filas_p1}
    filas, recs = [], []
    for etiq, x_b, P_alta, T_f, P_baja in PUNTOS_3:
        be = TeqpVerificado(x=x_b)
        f, dt = ciclo(be, x_b, P_alta, T_f, P_baja)
        f.update(etiqueta=etiq, x_b=x_b, P_alta=P_alta, T_fuente=T_f, P_baja=P_baja)
        e0 = ref.get(etiq, "")
        f.update(tiempo_s=round(dt, 2), n_recurrencias=len(be.recurrencias),
                 t_motor_real_s=round(be.t_real, 2), eta_teqp_puro=e0,
                 dEta=round(f["eta"] - e0, 8) if f["eta"] != "" and e0 != "" else "")
        filas.append(f)
        recs += [dict(etiqueta=etiq, **r) for r in be.recurrencias]
        log(f"  {etiq} P*={P_baja} eta={f['eta']} (teqp puro {e0}) t={dt:.1f}s "
            f"recurrencias={len(be.recurrencias)} t_real={be.t_real:.1f}s")
    escribir("parte3_verificado.csv", filas)
    escribir("parte3_recurrencias.csv", recs)
    return filas


def parte4(filas_p1, filas_p3, res2):
    log("PARTE 4 — tabla de costos y proyeccion a 30 puntos")
    t_teqp = st.mean(f["tiempo_s"] for f in filas_p1)
    t_3n = st.mean(f["tiempo_s"] for f in filas_p3 if f["etiqueta"].startswith("NORMAL"))
    t_3 = st.mean(f["tiempo_s"] for f in filas_p3)
    t_B = t_teqp + res2["h(P,s,x)"][0] + res2["T_from_Ps"][0]
    with open(SRC_VERIF, newline="", encoding="utf-8") as fh:
        reales = [float(r["tiempo_s"]) for r in csv.DictReader(fh) if r["motor"] == "real"]
    filas = [dict(opcion=o, s_por_punto=round(t, 2), s_30_puntos=round(30 * t, 1), base=b)
             for o, t, b in (
                 ("teqp puro (TeqpAdapter)", t_teqp, f"medido: {len(filas_p1)} ciclos con TeqpContado (Parte 1)"),
                 ("A: teqp verificado, 3 normales (sin recurrencia)", t_3n, "medido: 3 ciclos con TeqpVerificado (Parte 3)"),
                 ("A: teqp verificado, 5 puntos (con recurrencias)", t_3, "medido: 5 ciclos con TeqpVerificado (Parte 3)"),
                 ("B: teqp + verificacion final (h + T_from_Ps reales)", t_B, "medido: media teqp (P1) + media de 2 llamadas reales (P2)"),
                 ("motor real puro (AmmoniaWaterAdapter)", st.mean(reales), f"medido antes en {SRC_VERIF.parent.name} (n={len(reales)})"))]
    escribir("costo_tabla.csv", filas)
    n_z, n_i = sum(f["n_zona"] for f in filas_p1), sum(f["n_inv"] for f in filas_p1)
    n_t = sum(f["n_total"] for f in filas_p1)
    log(f"  zona: {n_z}/{n_i} inversiones ({100.0 * n_z / n_i:.2f}%), {n_z}/{n_t} "
        f"llamadas totales ({100.0 * n_z / n_t:.2f}%), puntos con zona: "
        f"{sum(1 for f in filas_p1 if f['n_zona'])}/{len(filas_p1)}")
    for f in filas:
        log(f"  {f['opcion']}: {f['s_por_punto']} s/punto, {f['s_30_puntos']} s/30 pts")
    return filas


def principal():
    OUT.mkdir(parents=True, exist_ok=True)
    log(f"zona: x_molar>={X_ALTO} y |T-Ta(P)|<{ZONA_T} K, o x_molar<={X_BAJO} y |T-Tw(P)|<{ZONA_T} K, con Ta,Tw = ng.Tsat_pure(P_pa)")
    filas_p1, turb = parte1()
    res2 = parte2(turb)
    parte4(filas_p1, parte3(filas_p1), res2)


if __name__ == "__main__":
    principal()
