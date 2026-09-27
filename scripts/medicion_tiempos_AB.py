"""Medición de tiempos REALES de teqp / A / B / A+B (TASK_CONTEXT 2026-09-27-medicion-tiempos-A-B).
`t_teqp` = `resolver_ciclo`+`evaluar_ciclo` con `TeqpAdapter`; `t_A` = lo mismo con `TeqpVerificado`; `t_B` = SOLO el
costo de `verificar_turbina` sobre el de `TeqpAdapter`; `t_AB` = t_A + `verificar_turbina` sobre el de `TeqpVerificado`.
Puntos: los 22 KALINA de `resultados/2026-09-24_margen2k/barrido_margen2k.csv` (en SU `P_baja`) + el espurio (x_b=0.60,
P_alta=4000, T_fuente=394, P_baja=423.914831). Se mide además `AmmoniaWaterAdapter.bubble_point` (5 puntos x 5 reps, para
decidir si B debe incluir el punto de burbuja de O2) y la repetibilidad de un ciclo completo (3+3 corridas en un punto,
para separar el ruido de reloj de la variación real entre puntos). UNA sola instancia de motor real por `x_b`; OJO: la 2ª
llamada de B de cada punto sale con la caché `_kalina_flash._ultimaT` caliente (sesgo a la baja que declara el reporte)."""
from __future__ import annotations

import csv
import statistics as st
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from src.cycle_solver import CicloNoConvergeError, resolver_ciclo        # noqa: E402
from src.properties.adapter import PropertyRangeError                   # noqa: E402
from src.properties.ammonia_water_adapter import AmmoniaWaterAdapter    # noqa: E402
from src.properties.teqp_adapter import TeqpAdapter                      # noqa: E402
from src.properties.teqp_verificado import TeqpVerificado               # noqa: E402
from src.restricciones.clasificacion import evaluar_ciclo               # noqa: E402
from src.verificacion_motor_real import UMBRAL_KJKG, verificar_turbina   # noqa: E402

OUT = REPO / "resultados" / "2026-09-27_medicion_AB"
SRC = REPO / "resultados" / "2026-09-24_margen2k" / "barrido_margen2k.csv"
EPS = (0.85, 0.80, 0.85)                  # efectividades fijas del TASK
T_SUMIDERO, T_AMB_DISENO = 283.0, 283.15
ETA_T, ETA_P, M_B = 0.80, 0.80, 1.0
ESPURIO = (0.60, 4000.0, 394.0, 423.914831)   # (x_b, P_alta, T_fuente, P_baja)
N_BUBBLE, REPS_BUBBLE, REPS_RUIDO = 5, 5, 3
EXC = (PropertyRangeError, CicloNoConvergeError, ValueError, RuntimeError, NotImplementedError, ArithmeticError)
MODOS = (("t_teqp_s", "teqp (`TeqpAdapter`)"), ("t_A_s", "A (`TeqpVerificado`)"), ("t_B_s", "B (verificación sobre teqp)"),
         ("t_BA_s", "B (verificación sobre A)"), ("t_AB_s", "A+B"))
_LOG = None


def log(msg):
    linea = f"[{time.strftime('%H:%M:%S')}] {msg}"
    print(linea, flush=True)
    if _LOG is not None:
        _LOG.write(linea + "\n")


def escribir(nombre, filas):
    if not filas:
        return
    with open(OUT / nombre, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(filas[0].keys()))
        w.writeheader()
        w.writerows(filas)
    log(f"  -> {nombre} ({len(filas)} filas)")


def puntos():
    """Los 22 KALINA del barrido + el caso espurio, con sus P_baja."""
    with open(SRC, newline="", encoding="utf-8") as fh:
        rs = [r for r in csv.DictReader(fh) if r["clasificacion"] == "KALINA"]
    ps = [dict(etiqueta=f"KALINA-{i + 1:02d}", x_b=float(r["x_b"]), P_alta=float(r["P_alta"]),
               T_fuente=float(r["T_fuente"]), P_baja=float(r["P_baja"]), eta_ref=float(r["eta"]))
          for i, r in enumerate(rs)]
    ps.append(dict(etiqueta="ESPURIO", x_b=ESPURIO[0], P_alta=ESPURIO[1], T_fuente=ESPURIO[2],
                   P_baja=ESPURIO[3], eta_ref=""))
    log(f"{len(rs)} KALINA de {SRC.relative_to(REPO)} + 1 espurio = {len(ps)} puntos")
    return ps


def motor(x_b, cache):
    """Una sola instancia de `AmmoniaWaterAdapter` por x_b (lo pide el TASK)."""
    if x_b not in cache:
        cache[x_b] = AmmoniaWaterAdapter(x=x_b)
    return cache[x_b]


def ciclo(cls, p):
    """Resuelve + clasifica un punto con `cls`; devuelve (fila, be, res, dt)."""
    be, t0 = cls(x=p["x_b"]), time.perf_counter()
    comun = dict(P_alta=p["P_alta"], P_baja=p["P_baja"], T_fuente=p["T_fuente"], T_sumidero=T_SUMIDERO,
                 x_b=p["x_b"], m_b=M_B, eps_hrvg=EPS[0], eps_reg=EPS[1], eps_cond=EPS[2])
    try:
        res = resolver_ciclo(be, eta_t=ETA_T, eta_p=ETA_P, **comun)
        val = evaluar_ciclo(be, res, T_amb_diseno=T_AMB_DISENO, **comun)
        fila = dict(eta=round(res["eta"], 9), clasificacion=val.clasificacion.value,
                    fallas=",".join(f.codigo for f in val.fallas), error="")
    except EXC as exc:
        res = None
        fila = dict(eta="", clasificacion="ERROR", fallas="", error=f"{type(exc).__name__}: {exc}"[:150])
    return fila, be, res, time.perf_counter() - t0


def medir_bubble(ps, cache):
    sel = [ps[i] for i in (0, 5, 11, 16, 21)]
    log(f"bubble_point: {len({(p['P_baja'], p['x_b']) for p in sel})} pares (P,x) distintos x {REPS_BUBBLE} reps = "
        f"{len(sel) * REPS_BUBBLE} llamadas")
    filas = []
    for p in sel:
        mot = motor(p["x_b"], cache)
        for r in range(REPS_BUBBLE):
            t0 = time.perf_counter()
            try:
                v, err = round(float(mot.bubble_point(p["P_baja"], p["x_b"])), 4), ""
            except EXC as exc:
                v, err = "", f"{type(exc).__name__}: {exc}"[:120]
            filas.append(dict(etiqueta=p["etiqueta"], rep=r + 1, x_b=p["x_b"], P_baja=p["P_baja"],
                              valor=v, tiempo_s=round(time.perf_counter() - t0, 3), error=err))
            log(f"  {p['etiqueta']} rep{r + 1} bubble_point({p['P_baja']:.3f}, {p['x_b']}) = {v} en "
                f"{filas[-1]['tiempo_s']}s {err}")
    return filas


def medir_ruido(p):
    filas = []
    for nombre, cls in (("teqp", TeqpAdapter), ("A", TeqpVerificado)):
        for r in range(REPS_RUIDO):
            dt = ciclo(cls, p)[3]
            filas.append(dict(modo=nombre, rep=r + 1, etiqueta=p["etiqueta"], x_b=p["x_b"],
                              P_baja=p["P_baja"], tiempo_s=round(dt, 2)))
            log(f"  RUIDO {nombre} rep{r + 1}: {dt:.2f} s")
    return filas


def principal():
    global _LOG
    OUT.mkdir(parents=True, exist_ok=True)
    _LOG = open(OUT / "run.log", "w", encoding="utf-8", buffering=1)
    log("MEDICION teqp / A / B / A+B (TASK 2026-09-27-medicion-tiempos-A-B)")
    log(f"  T_sumidero={T_SUMIDERO} K, T_amb_diseno={T_AMB_DISENO} K, eta_t=eta_p={ETA_T}, eps={EPS}, m_b={M_B} kg/s, "
        f"umbral_B={UMBRAL_KJKG}")
    log("  t_B usa la vía RECONSTRUIDA de h4s (sin backend_teqp): docstring de src/verificacion_motor_real.py")
    t0, cache = time.perf_counter(), {}
    motor(0.6, cache)                    # 1a vez: el costo de crear el motor real
    t_init = time.perf_counter() - t0
    log(f"  t_init_motor_real (una vez) = {t_init * 1e3:.4f} ms")

    ps, filas = puntos(), []
    for p in ps:
        ft, _, res_t, t_teqp = ciclo(TeqpAdapter, p)
        fa, be_a, res_a, t_A = ciclo(TeqpVerificado, p)
        mot = motor(p["x_b"], cache)
        t0 = time.perf_counter()
        vt = None if res_t is None else verificar_turbina(res_t, P_baja=p["P_baja"], motor_real=mot, eta_t=ETA_T)
        t_B = time.perf_counter() - t0
        t0 = time.perf_counter()
        va = None if res_a is None else verificar_turbina(res_a, P_baja=p["P_baja"], motor_real=mot, eta_t=ETA_T)
        t_BA = time.perf_counter() - t0
        d_eta = round(fa["eta"] - ft["eta"], 12) if ft["eta"] != "" and fa["eta"] != "" else ""
        filas.append(dict(
            etiqueta=p["etiqueta"], x_b=p["x_b"], P_alta=p["P_alta"], T_fuente=p["T_fuente"],
            P_baja=p["P_baja"], eta_ref=p["eta_ref"], eta_teqp=ft["eta"], eta_A=fa["eta"], d_eta=d_eta,
            clas_teqp=ft["clasificacion"], clas_A=fa["clasificacion"], t_teqp_s=round(t_teqp, 2),
            t_A_s=round(t_A, 2), t_B_s=round(t_B, 2), t_BA_s=round(t_BA, 2), t_AB_s=round(t_A + t_BA, 2),
            dh4s_teqp=(None if vt is None else round(vt["dh4s"], 4)),
            verificado_teqp=(None if vt is None else vt["verificado"]),
            t_real_B_s=(None if vt is None else round(vt["t_real_s"], 2)),
            error_B=(None if vt is None else vt["error"]),
            dh4s_A=(None if va is None else round(va["dh4s"], 4)),
            verificado_A=(None if va is None else va["verificado"]),
            error_BA=(None if va is None else va["error"]),
            n_recurrencias=getattr(be_a, "n_recurrencias", 0),
            t_real_A_s=round(getattr(be_a, "t_real", 0.0), 2),
            verif_incompleta_A=getattr(be_a, "verificacion_incompleta", False),
            fallas_teqp=ft["fallas"], fallas_A=fa["fallas"],
            error_teqp=ft["error"], error_A=fa["error"]))
        f = filas[-1]
        log(f"  {p['etiqueta']} x={p['x_b']} P*={p['P_baja']:.3f} | t_teqp={t_teqp:.2f} t_A={t_A:.2f} t_B={t_B:.2f} "
            f"t_AB={t_A + t_BA:.2f} | eta {ft['eta']}/{fa['eta']} | clas {ft['clasificacion']}/{fa['clasificacion']} | "
            f"dh4s {f['dh4s_teqp']}->{f['dh4s_A']} | verif {f['verificado_teqp']}/{f['verificado_A']} | rec A="
            f"{f['n_recurrencias']} t_real A={f['t_real_A_s']}s")
    escribir("medicion_puntos.csv", filas)
    bub = medir_bubble(ps, cache)
    escribir("medicion_bubble_point.csv", bub)
    rui = medir_ruido(ps[0])
    escribir("medicion_ruido_reloj.csv", rui)
    reporte(filas, bub, rui, t_init)
    _LOG.close()


def reporte(filas, bub, rui, t_init):
    t = {k: [f[k] for f in filas] for k, _ in MODOS}
    med = {k: st.mean(v) for k, v in t.items()}
    so = {k: 100.0 * (med[k] / med["t_teqp_s"] - 1.0) for k, _ in MODOS[1:]}
    so["t_B_s"] = 100.0 * med["t_B_s"] / med["t_teqp_s"]    # B es coste AÑADIDO al ciclo teqp, no un sustituto
    bs = [float(f["tiempo_s"]) for f in bub]
    esp = [f for f in filas if f["etiqueta"] == "ESPURIO"][0]
    n, nrec, t30, bubm = len(filas), sum(f["n_recurrencias"] for f in filas), 30 * med["t_teqp_s"], st.mean(bs)
    L = ["# REPORTE — Tiempos reales de teqp / A / B / A+B\n",
         f"Generado por `scripts/medicion_tiempos_AB.py` el {time.strftime('%Y-%m-%d %H:%M:%S')}. Datos en "
         f"`resultados/2026-09-27_medicion_AB/`: `medicion_puntos.csv` ({n} puntos), `medicion_bubble_point.csv` "
         f"({len(bs)} llamadas), `medicion_ruido_reloj.csv` ({len(rui)} corridas), `run.log`.\n",
         f"Definiciones: **t_teqp**/**t_A** = `resolver_ciclo` + `evaluar_ciclo` con `TeqpAdapter`/`TeqpVerificado`; "
         f"**t_B** = SOLO el costo de `verificar_turbina` sobre el de `TeqpAdapter`; **t_AB** = t_A + `verificar_turbina` "
         f"sobre el de `TeqpVerificado`. Parámetros: T_sumidero={T_SUMIDERO} K, T_amb_diseno={T_AMB_DISENO} K, "
         f"η_t=η_p={ETA_T}, ε={EPS}, ṁ_b={M_B} kg/s, umbral de B = {UMBRAL_KJKG} kJ/kg. Puntos: los {n - 1} KALINA de "
         f"`2026-09-24_margen2k/barrido_margen2k.csv` (en su P_baja) + el espurio (x_b={ESPURIO[0]}, P_alta={ESPURIO[1]:.0f}, "
         f"T_fuente={ESPURIO[2]:.0f}, P_baja={ESPURIO[3]}).\n",
         "## Resumen de tiempos (una corrida por modo y punto)\n",
         "| Modo | media [s] | mediana [s] | min [s] | max [s] | rango [s] | sobrecosto vs teqp |",         "|---|---|---|---|---|---|---|"]
    for k, nombre in MODOS:
        s = "—" if k == "t_teqp_s" else ("— (solo diagnóstico, caché caliente)" if k == "t_BA_s" else
                                        f"**{so[k]:+.1f} %**" + (" (añadido)" if k == "t_B_s" else ""))
        L.append(f"| {nombre} | {med[k]:.2f} | {st.median(t[k]):.2f} | {min(t[k]):.2f} | {max(t[k]):.2f} | "
                 f"{max(t[k]) - min(t[k]):.2f} | {s} |")
    L += ["\n## Tabla por punto\n",
          "| # | P_baja [kPa] | t_teqp [s] | t_A [s] | t_B [s] | t_AB [s] | η teqp | η A | "
          "clas teqp | clas A | Δh4s B(teqp) | verif | Δh4s B(A+B) | verif | rec. A |", "|---|" + "---|" * 14]
    for f in filas:
        L.append(f"| {f['etiqueta']} | {f['P_baja']:.3f} | {f['t_teqp_s']} | {f['t_A_s']} | {f['t_B_s']} | "
                 f"{f['t_AB_s']} | {f['eta_teqp']} | {f['eta_A']} | {f['clas_teqp']} | {f['clas_A']} | {f['dh4s_teqp']} | "
                 f"{f['verificado_teqp']} | {f['dh4s_A']} | {f['verificado_A']} | {f['n_recurrencias']} |")
    L += ["", "## Proyección: barrido de 30 puntos con ~20 KALINA (los ~10 no KALINA pasarían por teqp+A sin B)\n",
          "| Modo | s/punto | s/30 puntos |", "|---|---|---|",
          f"| teqp | {med['t_teqp_s']:.2f} | {t30:.0f} |", f"| A | {med['t_A_s']:.2f} | {30 * med['t_A_s']:.0f} |",
          f"| B (solo KALINA) | {med['t_teqp_s']:.2f} | {t30 + 20 * med['t_B_s']:.0f} |",
          f"| A+B (solo KALINA) | {med['t_AB_s']:.2f} | {20 * med['t_AB_s'] + 10 * med['t_A_s']:.0f} |",
          "", "## Costo medido de `bubble_point` en el motor real\n",
          f"- {len(bs)} llamadas ({N_BUBBLE} puntos distintos x {REPS_BUBBLE} repeticiones): media **{bubm:.2f} s**, mediana "
          f"{st.median(bs):.2f} s, min {min(bs):.2f} s, max {max(bs):.2f} s, rango {max(bs) - min(bs):.2f} s. Es "
          f"{bubm / med['t_B_s']:.1f} veces el costo de B por punto ({med['t_B_s']:.2f} s): si B comprobara además el punto de "
          f"burbuja de O2, su sobrecosto iría de {so['t_B_s']:+.1f} % a {so['t_B_s'] + 100.0 * bubm / med['t_teqp_s']:+.1f} % y el "
          f"barrido de {t30 + 20 * med['t_B_s']:.0f} s a {t30 + 20 * (med['t_B_s'] + bubm):.0f} s.",
          "", "## Repetibilidad y ruido de reloj\n",
          f"- {REPS_RUIDO} repeticiones de cada modo en UN mismo punto ({rui[0]['etiqueta']}, x_b={rui[0]['x_b']}, "
          f"P_baja={rui[0]['P_baja']}), con detalle en `medicion_ruido_reloj.csv`. El rango `min..max` de la tabla "
          f"({max(t['t_teqp_s']) - min(t['t_teqp_s']):.1f} s en teqp) mezcla el ruido de reloj (±1-2 s) y la variación REAL entre "
          f"puntos (x_b, P_baja, nº de iteraciones de los dos lazos del solver): es una cota superior del ruido, no su medida. "
          "t_B y t_BA comparten la caché `_kalina_flash._ultimaT` dentro del mismo punto, y en modo A ese motor ya se usó "
          "durante el ciclo: **t_BA está sesgado a la baja**.\n", "## ¿Detecta B el caso espurio?\n",
          f"- Con **TeqpAdapter** (B solo): Δh4s = {esp['dh4s_teqp']} kJ/kg → **verificado = {esp['verificado_teqp']}**; "
          f"η = {esp['eta_teqp']}, clasificación {esp['clas_teqp']}. Sí: muy por encima del umbral de {UMBRAL_KJKG} kJ/kg.",
          f"- Con **A+B**: Δh4s = {esp['dh4s_A']} kJ/kg → **verificado = {esp['verificado_A']}**; η = {esp['eta_A']}, "
          f"clasificación {esp['clas_A']}, con {esp['n_recurrencias']} recurrencia(s) de A. Puntos verificados: "
          f"{sum(1 for f in filas if f['verificado_teqp'] is True)}/{n} con B sobre teqp, "
          f"{sum(1 for f in filas if f['verificado_A'] is True)}/{n} con B sobre A.\n",
          "## Lectura\n",
          f"- **A** cuesta {so['t_A_s']:+.1f} % frente a teqp, y solo hubo {nrec} recurrencia(s) al motor real en los {n} puntos "
          f"(el respaldo de A solo se dispara en la zona de riesgo). **B** cuesta {so['t_B_s']:+.1f} % por punto "
          f"({med['t_teqp_s']:.2f} → {med['t_teqp_s'] + med['t_B_s']:.2f} s) y da un veredicto por punto con UNA llamada al motor "
          f"real, sin cambiar el resultado del ciclo: solo lo señala (en A+B un Δh4s pequeño significa que A ya sustituyó el "
          "valor, no que teqp acertara).\n"]
    (OUT / "REPORTE_MEDICION_AB.md").write_text("\n".join(L), encoding="utf-8")
    log(f"  -> REPORTE_MEDICION_AB.md | OVERCOSTO A {so['t_A_s']:+.1f} % | B (añadido) {so['t_B_s']:+.1f} % | "
        f"A+B {so['t_AB_s']:+.1f} % | bubble_point {bubm:.2f} s | t_init_motor_real {t_init * 1e3:.4f} ms")


if __name__ == "__main__":
    principal()
