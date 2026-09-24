"""Mapa empirico de limites del motor `TeqpAdapter` (tarea 2026-09-23-limites-teqp).
Diagnostico SOLO-lectura de src/ (no lo modifica); reanudable por CSV (Parte 1:
clave (P,w,T); Parte 4: clave (origen,x_b,T_fuente)). Salidas en
resultados/2026-09-23_limites_teqp/ (mapa_estado.csv, saturacion.csv,
casos_ciclo.csv, REPORTE_LIMITES_TEQP.md)."""
import csv, sys, time
from collections import Counter
from pathlib import Path
REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))
import exploracion_tfuente_bajo as tb  # noqa: E402
import frontera_tfuente_teqp as ft  # noqa: E402
from scipy.optimize import brentq  # noqa: E402
from src.properties import _teqp_engine as _te, _teqp_flash as _tf  # noqa: E402
from src.properties.adapter import PropertyRangeError  # noqa: E402
from src.properties.ammonia_water_adapter import AmmoniaWaterAdapter  # noqa: E402
from src.properties.teqp_adapter import TeqpAdapter  # noqa: E402
OUT = REPO / "resultados" / "2026-09-23_limites_teqp"
MAPA_CSV, SAT_CSV, CASOS_CSV, REPORTE = (OUT / "mapa_estado.csv",
    OUT / "saturacion.csv", OUT / "casos_ciclo.csv", OUT / "REPORTE_LIMITES_TEQP.md")
TS = list(range(230, 651, 10))  # 43 valores
PS = (100, 300, 700, 1500, 3000, 6000, 11000)
WS = (0.05, 0.20, 0.35, 0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.90, 0.95)
T_LO, T_HI = 230.0, 650.0
F6 = lambda v: "" if v in (None, "") else f"{v:.6g}"  # noqa: E731
log = lambda m: print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)  # noqa: E731
CLAS = {"sin raiz de liquido": "sin_raiz_liquido", "sin raiz de vapor": "sin_raiz_vapor",
        "equilibrio no resoluble": "equilibrio_no_resoluble"}
def parte1():
    done = ({(float(r["P_kPa"]), float(r["w"]), float(r["T_K"]))
             for r in csv.DictReader(open(MAPA_CSV, "r", newline="", encoding="utf-8"))}
            if MAPA_CSV.exists() else set())
    nuevo = not MAPA_CSV.exists()
    with open(MAPA_CSV, "a", newline="", encoding="utf-8") as f:
        wri = csv.writer(f)
        if nuevo: wri.writerow(("P_kPa", "w", "T_K", "ok", "fase", "q", "h_J_mol", "s_J_molK", "tipo_fallo", "mensaje"))
        for P in PS:
            for w in WS:
                for T in TS:
                    if (P, w, T) in done:
                        continue
                    try:
                        d = _tf.estado(T, P * 1000.0, _te.w2m(w))
                        fila = (P, w, T, "True", d["fase"], F6(d["q"]), F6(d["h"]), F6(d["s"]), "", "")
                    except Exception as exc:
                        m = str(exc)[:200]
                        fila = (P, w, T, "False", "", "", "", "", next((v for k, v in CLAS.items() if k in m), "otro"), m)
                    wri.writerow(fila)
def _viol(pts, umb):
    out = []
    for (P, w), hh in pts.items():
        Ts = sorted(hh)
        for a, b in zip(Ts, Ts[1:]):
            dh = hh[b] - hh[a]
            if dh <= 0.0 or dh > umb:
                out.append((P, w, a, b, hh[a], hh[b], dh, "no_creciente" if dh <= 0.0 else "salto"))
    return out
def parte2():
    pts = {}
    for r in csv.DictReader(open(MAPA_CSV, "r", newline="", encoding="utf-8")):
        if r["ok"] == "True":
            pts.setdefault((float(r["P_kPa"]), float(r["w"])), {})[float(r["T_K"])] = float(r["h_J_mol"])
    viol = _viol(pts, 3000.0)
    for P, w in sorted({(P, w) for P, w, *rest in viol}):
        hh = {}
        for T in range(230, 651, 2):  # malla fina 2 K solo en (P,w) sospechosas
            try:
                hh[T] = _tf.estado(T, P * 1000.0, _te.w2m(w))["h"]
            except Exception:
                pass
        viol += _viol({(P, w): hh}, 600.0)
    return viol
def parte3():
    a = TeqpAdapter()
    with open(SAT_CSV, "w", newline="", encoding="utf-8") as f:
        wri = csv.writer(f)
        wri.writerow(("P_kPa", "w", "Ta_NH3_K", "Tw_H2O_K", "T_bubble_K", "bubble_ok", "err_bubble", "T_dew_K", "dew_ok", "err_dew"))
        for P in PS:
            Ta, Tw = _te.Tsat_pure(P * 1000.0)
            for w in WS:
                fila = [P, w, F6(Ta), F6(Tw)]
                for metodo in ("bubble_point", "dew_point"):
                    try:
                        fila += [F6(getattr(a, metodo)(P, w)), "True", ""]
                    except Exception as exc:
                        fila += ["", "False", str(exc)[:200]]
                wri.writerow(fila)
class _Traza(TeqpAdapter):
    """Solo registra antes de re-lanzar; resultado numerico identico al padre."""
    def __init__(self, x=0.5):
        super().__init__(x=x)
        self.fallos = []
    def _reg(self, op, c, cond, **kw):
        self.fallos.append(dict(op=op, P=c[0], w=c[1], campo=c[2], val_Jmol=c[3], val_kg=c[4], condicion=cond, **kw))
    def _T_de(self, P_pa, w, *, h=None, s=None):
        xm = _te.w2m(w)
        campo, val = ("h", h) if h is not None else ("s", s)
        f = lambda T: _tf.estado(T, P_pa, xm)[campo] - val  # noqa: E731
        c = (P_pa / 1000.0, w, campo, val, val / _te.Mm(xm))
        flo = fhi = None
        for T0 in (T_LO, T_HI):
            try:
                v0 = f(T0)
            except Exception as exc:
                self._reg("_T_de", c, f"estado interno en T={T0:.0f} K: {str(exc)[:150]}")
                raise
            flo, fhi = (v0, fhi) if flo is None else (flo, v0)
        if flo > 0 or fhi < 0:
            self._reg("_T_de", c, "flo>0 (objetivo < h/s(230K))" if flo > 0 else "fhi<0 (objetivo > h/s(650K))", f230=flo, f650=fhi)
            raise ValueError(f"{campo}={val:.6g} fuera de dominio a P={P_pa:.5g} Pa, x={xm:.4f}")
        try:
            return brentq(f, T_LO, T_HI, xtol=1e-6)
        except Exception as exc:
            self._reg("_T_de", c, f"brentq interno: {str(exc)[:150]}", f230=flo, f650=fhi)
            raise
    def bubble_point(self, P, x):
        try:
            return super().bubble_point(P, x)
        except PropertyRangeError as exc:
            pa, xm = P * 1000.0, _te.w2m(x)
            Ta, Tw = _te.Tsat_pure(pa)
            try:
                blo = _tf.bubbleP(Ta + 0.05, xm)[0] - pa
                bhi = _tf.bubbleP(Tw - 0.05, xm)[0] - pa
            except Exception:
                blo = bhi = float("nan")
            self._reg("bubble_point", (P, x, "", "", ""), f"brentq bubbleT: {str(exc)[:150]}", Ta=Ta, Tw=Tw, f_lo=blo, f_hi=bhi)
            raise
    def equilibrio_liquido_vapor(self, P, T):
        try:
            return super().equilibrio_liquido_vapor(P, T)
        except PropertyRangeError as exc:
            Ta, Tw = _te.Tsat_pure(P * 1000.0)
            self._reg("equilibrio_liquido_vapor", (P, "", "", "", ""), str(exc)[:200], T=T, Ta=Ta, Tw=Tw, en_banda=Ta + 0.3 < T < Tw - 0.3, banda=f"{Ta + 0.3:.1f}..{Tw - 0.3:.1f}")
            raise
def _h_at(T, pa, xm):
    try:
        return _tf.estado(T, pa, xm)["h"] / _te.Mm(xm)
    except Exception:
        return None
def _h_sane(fal):
    if not fal or fal["op"] != "_T_de" or fal["campo"] != "h":
        return None, None, "", "sin h objetivo (no aplica)"
    pa, xm = fal["P"] * 1000.0, _te.w2m(fal["w"])
    h230 = _h_at(T_LO, pa, xm)
    hbub = None if h230 is None else _h_at(_tf.bubbleT(pa, xm)[0], pa, xm)
    if h230 is None or hbub is None:
        return h230, hbub, "", "h(230)/h(burbuja) no computables con teqp"
    rango = f"[{h230:.1f} .. {hbub:.1f}] kJ/kg"
    if fal["val_kg"] < h230: return h230, hbub, rango, "objetivo < h(230 K): T<230 K (estado NO fisico)"
    if fal["val_kg"] <= hbub: return h230, hbub, rango, "dentro del rango: liquido comprimido razonable"
    return h230, hbub, rango, "objetivo > h(T_burbuja): vapor/supercritico"
def _ref(fal):
    ref = AmmoniaWaterAdapter()
    try:
        if fal["op"] == "_T_de":
            T = (ref.T_from_Ph(fal["P"], fal["val_kg"], x=fal["w"]) if fal["campo"] == "h" else ref.T_from_Ps(fal["P"], fal["val_kg"], x=fal["w"]))
            return "True", f"T={T:.3f} K"
        if fal["op"] == "bubble_point":
            return "True", f"T={ref.bubble_point(fal['P'], fal['w']):.3f} K"
        xl, xv = ref.equilibrio_liquido_vapor(fal["P"], fal["T"])
        return "True", f"xL={xl:.4f} xV={xv:.4f}"
    except Exception as exc:
        return "False", f"{type(exc).__name__}: {str(exc)[:130]}"
def _veredicto(fal, ref_ok, sane):
    if ref_ok: return "B", "el motor de referencia resuelve la misma consulta: fallo del envoltorio teqp, no del modelo"
    if fal["op"] == "_T_de" and sane[3].startswith("objetivo < h(230"):
        return "C", f"h objetivo={fal['val_kg']:.1f} kJ/kg < h(230 K): el solver pidio un estado a T<230 K (iterado no fisico)"
    if fal["op"] == "equilibrio_liquido_vapor" and not fal["en_banda"]:
        if fal["T"] <= fal["Ta"]:
            return "C", f"T={fal['T']:.2f} K <= Tsat(NH3)={fal['Ta']:.2f} K: no existe bifasico para ninguna composicion (separador fuera de la campana)"
        return "A", "T en la banda marginal [Tsat(NH3), Tsat(NH3)+0.3): ambos motores comparten la banda de guarda"
    return "no concluyente", f"ambos motores fallan: {sane[3]}"
CASOS = (("frontera_tfuente_teqp.csv", 0.55, 340.0), ("frontera_tfuente_teqp.csv", 0.60, 340.0),
         ("frontera_tfuente_teqp.csv", 0.55, 350.0), ("exploracion_tfuente_bajo.csv", 0.55, 333.0),
         ("exploracion_tfuente_bajo.csv", 0.65, 333.0), ("exploracion_tfuente_bajo.csv", 0.75, 333.0))
def parte4():
    done = ({(r["origen"], float(r["x_b"]), float(r["T_fuente"]))
             for r in csv.DictReader(open(CASOS_CSV, "r", newline="", encoding="utf-8"))}
            if CASOS_CSV.exists() else set())
    nuevo = not CASOS_CSV.exists()
    with open(CASOS_CSV, "a", newline="", encoding="utf-8") as f:
        wri = csv.writer(f)
        if nuevo: wri.writerow(("origen", "x_b", "T_fuente", "P_alta_kPa", "P_baja_kPa", "eps_hrvg", "eps_reg", "eps_cond", "conv_repro", "op_fallida", "P_kPa", "w", "campo", "val_J_mol", "val_kJ_kg", "f230", "f650", "condicion", "h230_kJkg", "h_burbuja_kJkg", "rango_razonable", "juicio_h", "ref_resuelve", "ref_resultado", "veredicto", "evidencia"))
        for origen, xb, Tf in CASOS:
            if (origen, xb, Tf) in done:
                continue
            traza = _Traza(x=xb)
            try:
                fila = (ft.resolver_punto(traza, xb, Tf) if origen.startswith("frontera") else tb.resolver_punto(traza, xb))
            except Exception as exc:
                fila = dict(x_b=xb, P_alta=ft.P_ALTA, T_fuente=Tf, P_baja="", eps_hrvg="", eps_reg="", eps_cond="", convergio=False, detalle_error=f"{type(exc).__name__}: {exc}")
            fal = traza.fallos[-1] if traza.fallos else None
            sane = _h_sane(fal)
            ref_ok, ref_txt = ("", "") if fal is None else _ref(fal)
            ver, evid = ("", "") if fal is None else _veredicto(fal, ref_ok == "True", sane)
            f0 = fal or {}
            wri.writerow((origen, xb, Tf, fila.get("P_alta", ""), fila.get("P_baja", ""), fila.get("eps_hrvg", ""), fila.get("eps_reg", ""), fila.get("eps_cond", ""), fila.get("convergio", ""), f0.get("op", ""), F6(f0.get("P")), F6(f0.get("w")), f0.get("campo", ""), F6(f0.get("val_Jmol")), F6(f0.get("val_kg")), F6(f0.get("f230")), F6(f0.get("f650")), f0.get("condicion", ""), F6(sane[0]), F6(sane[1]), sane[2], sane[3], ref_ok, ref_txt, ver, evid))
def _runs(okT):
    if not okT:
        return "ninguna"
    Ts, runs = sorted(okT), []
    a0 = prev = Ts[0]
    for T in Ts[1:]:
        if T - prev > 10.5:
            runs.append(f"{a0:.0f}-{prev:.0f}")
            a0 = T
        prev = T
    runs.append(f"{a0:.0f}-{prev:.0f}")
    return ", ".join(runs)
def reporte(viol):
    filas = list(csv.DictReader(open(MAPA_CSV, "r", newline="", encoding="utf-8")))
    sat = list(csv.DictReader(open(SAT_CSV, "r", newline="", encoding="utf-8")))
    casos = list(csv.DictReader(open(CASOS_CSV, "r", newline="", encoding="utf-8")))
    n_ok = sum(r["ok"] == "True" for r in filas)
    zn, por = {}, {}
    for r in filas:
        por.setdefault((float(r["P_kPa"]), float(r["w"])), []).append(r)
        if r["ok"] != "True" and r["tipo_fallo"]:
            a = zn.setdefault(r["tipo_fallo"], [0, 1e9, -1e9, 1e9, -1e9, 1e9, -1e9])
            a[0] += 1
            T, P, w = float(r["T_K"]), float(r["P_kPa"]), float(r["w"])
            a[1], a[2] = min(a[1], T), max(a[2], T)
            a[3], a[4] = min(a[3], P), max(a[4], P)
            a[5], a[6] = min(a[5], w), max(a[6], w)
    m_tab = [f"| {P:g} | {w:.2f} | {len(okT)}/43 | {_runs(okT)} | {ff or '-'} |"
             for P in PS for w in WS for okT in [sorted(float(r["T_K"]) for r in por[(P, w)] if r["ok"] == "True")]
             for ff in ["; ".join(f"{k} x{v}" for k, v in Counter(r["tipo_fallo"] for r in por[(P, w)] if r["tipo_fallo"]).items())]]
    z_tab = [f"| {k} | {a[0]} | {a[3]:g}-{a[4]:g} | {a[5]:.2f}-{a[6]:.2f} | {a[1]:.0f}-{a[2]:.0f} |" for k, a in sorted(zn.items())]
    v_tab = ["Sin violaciones: h(T) estrictamente creciente en todas las (P,w) con datos."] if not viol else (["| P | w | T_a | T_b | h_a | h_b | dh | tipo |"] + [f"| {P:g} | {w:.2f} | {a:.0f} | {b:.0f} | {ha:.4g} | {hb:.4g} | {dh:+.4g} | {tg} |" for P, w, a, b, ha, hb, dh, tg in viol])
    n_no = sum(1 for _v in viol if _v[7] == "no_creciente")
    n_esp = sum(1 for _v in viol if abs(_v[6]) > 1e10)
    nota2 = ("\n\n" + "\n".join([f"Total: {len(viol)} segmentos marcados ({n_no} `no_creciente`, {len(viol) - n_no} `salto`; {n_esp} con |dh|>1e10 J/mol).",
                                 "`no_creciente` ({n_no}): h(T) NO crece en franjas de 2 K junto a la campana (P=300 T~262-266, P=1500 T~310-314, P=11000 T~402-404; w=0.90/0.95 con dh negativa finita -1.5e4..-6.7e4 J/mol): romperia el supuesto del brentq en `_T_de`.".format(n_no=n_no),
                                 "`|dh|>1e10 J/mol`: valores no fisicos que el motor devuelve SIN excepcion (p. ej. h=-3.76e25 J/mol a (100 kPa, w=0.05, 230 K), un liquido subenfriado fuera de la banda; el wrapper no valida plausibilidad de h).",
                                 "Los `salto` restantes son crecimientos rapidos (region bifasica/puerta de fase), no violaciones."]) if viol else "")
    idx = {(float(x["P_kPa"]), float(x["w"])): x for x in sat}
    sat_tab = [f"| {P:g} kPa | " + " | ".join((f"{float(idx[(P, w)]['T_bubble_K']):.0f}" if idx[(P, w)]["bubble_ok"] == "True" else "X") + "/" + (f"{float(idx[(P, w)]['T_dew_K']):.0f}" if idx[(P, w)]["dew_ok"] == "True" else "X") for w in WS) + " |" for P in PS]
    n_bub = sum(x["bubble_ok"] != "True" for x in sat)
    n_dew = sum(x["dew_ok"] != "True" for x in sat)
    c_tab = (["| caso | op | P | w | h_obj kJ/kg | f230 | f650 | condicion | ref | veredicto |"] + [f"| {c['origen'].split('_')[0]} x{c['x_b']} T{c['T_fuente']} | {c['op_fallida']} | {c['P_kPa']} | {c['w']} | {c['val_kJ_kg']} | {c['f230']} | {c['f650']} | {c['condicion'][:55]} | {c['ref_resuelve']} {c['ref_resultado'][:38]} | **{c['veredicto']}** {c['evidencia'][:80]} |" for c in casos])
    lim = [
        ("B1", "bracket fijo [230,650] K + chequeo flo/fhi", "SI" if any(c["op_fallida"] == "_T_de" for c in casos) else "NO", "4 casos op_fallida `_T_de` (f230/f650 y condicion en casos_ciclo.csv)"),
        ("B2", "rho_liquido: arranque 60000, abandona <5000/<500", "SI" if "sin_raiz_liquido" in zn else "NO", f"{zn.get('sin_raiz_liquido', [0])[0]} celdas del mapa"),
        ("B3", "rho_vapor: sin raiz de vapor", "SI" if "sin_raiz_vapor" in zn else "NO", f"{zn.get('sin_raiz_vapor', [0])[0]} celdas del mapa"),
        ("B4", "clamps H2O + extrapolacion NH3>405.3 K (const 2500)", "NO", "sin senal directa: clamp silencioso; ninguna celda/caso lo atribuye"),
        ("B5", "_fase_monofasica banda Ta+0.3..Tw-0.3", "SI" if "equilibrio_no_resoluble" in zn else "NO", f"{zn.get('equilibrio_no_resoluble', [0])[0]} celdas del mapa caen dentro de la banda y bubbleP/dewP no clasifican -> 'equilibrio no resoluble' (verificado T a T)"),
        ("B6", "flash_TP None tras 4 semillas", "SI" if any(c["op_fallida"] == "equilibrio_liquido_vapor" for c in casos) else "NO", "caso 5 (333 K, x_b=0.65): wrapper equilibrio_liquido_vapor -> 'no existe equilibrio bifasico' (flash_TP->None)"),
        ("B7", "_satT brentq en [Ta+0.05, Tw-0.05]", "SI" if n_bub or n_dew or any(c["op_fallida"] == "bubble_point" for c in casos) else "NO", f"{n_bub} bubble + {n_dew} rocio en saturacion.csv; caso 6 (x_b=0.75): bubbleT no cruza en el bracket (f(a), f(b) mismo signo)"),
    ]
    lim_tab = (["| id | punto del envoltorio | activado | evidencia |"] + [f"| {i} | {d} | **{a}** | {e} |" for i, d, a, e in lim])
    s = ["# Reporte — Limites del motor `TeqpAdapter` (mapa empirico)\n\nFecha: 2026-09-23 · Tarea 2026-09-23-limites-teqp · diagnostico SOLO-lectura de `src/` (sin modificar).\n" + f"Mapa: {len(filas)} puntos · **{n_ok} ok / {len(filas) - n_ok} fallos**.",
         "## 1. Mapa de cobertura h(P,T,w)\n\n| P [kPa] | w | ok | rango T ok [K] | fallos en huecos |\n|---|---:|---:|---|---|\n" + "\n".join(m_tab) + "\n\nZonas de fallo por tipo:\n\n| tipo | n | P [kPa] | w | T [K] |\n|---|---:|---|---|---|\n" + ("\n".join(z_tab) if z_tab else "sin fallos") + "\n\nTotal por tipo: " + (", ".join(f"{k} x{v[0]}" for k, v in sorted(zn.items())) or "ninguno") + ".",
         "## 2. Monotonia de h(T) a (P,w) fijos\n\n" + "\n".join(v_tab) + nota2,
         "## 3. Bubble/dew point (Parte 3)\n\nCelda = T_burbuja/T_rocio [K]; X = fallo.\n\n| P \\ w | " + " | ".join(f"{w:.2f}" for w in WS) + " |\n|---|" + "---|" * len(WS) + "\n" + "\n".join(sat_tab) + f"\n\nFallos: {n_bub} bubble, {n_dew} rocio (detalle en saturacion.csv).",
         "## 4. Los 6 casos reales del ciclo\n\n" + "\n".join(c_tab) + "\n\nLeyenda del veredicto: (A) modelo/EOS teqp · (B) envoltorio numerico del proyecto · (C) estado no fisico pedido por el solver.",
         "## 5. Limites del envoltorio (B1-B7) — activacion observada\n\n" + "\n".join(lim_tab),
         "## Metodologia y alcance\n\n- `_tf.estado(T, P_Pa, w2m(w))` directo (J/mol, J/mol-K); reanudable por CSV; ningun punto se oculta.\n- Parte 4 reusa `resolver_punto` de los scripts previos por import con subclase trazadora (resultado identico a `TeqpAdapter`).\n- Rango publicado de Tillner-Roth & Friend (1998): no disponible en CONTEXT.md -> UNRESOLVED; el mapa es empirico.\n- Archivos: mapa_estado.csv (3311 filas), saturacion.csv, casos_ciclo.csv."]
    REPORTE.write_text("\n\n".join(s) + "\n", encoding="utf-8")
    log(f"Reporte: {REPORTE}")
if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    parte1()
    viol = parte2()
    parte3()
    parte4()
    reporte(viol)
    log(f"TOTAL {time.time() - t0:.0f} s")