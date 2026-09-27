"""Verificación de los dos motores NH3-H2O contra las Tablas 6-8 de IAPWS G4-01
(Tillner-Roth & Friend, 1998): referencia `_nh3h2o_engine.py` (MPa, mol/dm3) y
teqp `_teqp_engine.py`+`_teqp_flash.py` (Pa, mol/m3) en los 12 puntos de la guía (§8)."""
import csv, sys
from pathlib import Path
import numpy as np
sys.stdout.reconfigure(encoding="utf-8")
REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from src.properties import _nh3h2o_engine as ng  # noqa: E402
from src.properties import _teqp_engine as te    # noqa: E402
from src.properties import _teqp_flash as tf     # noqa: E402
OUT = REPO / "resultados" / "2026-09-23_verificacion_iapws_g4"
CSV_PATH = OUT / "verificacion_iapws_g4.csv"
REP_PATH = OUT / "REPORTE_VERIFICACION_IAPWS_G4.md"
COLS = ("motor", "tabla", "punto", "propiedad", "valor_guia", "valor_motor", "error_abs", "error_rel", "tolerancia", "cumple", "detalle")
MOTORES = ("iapws", "teqp")
# transcritos de IAPWS G4-01 §8. x, T[K], rho[mol/dm3], f[J/mol], p[MPa], Cv[J/molK], w[m/s]
T6 = ((0.1, 600, 35, -13734.1763, 32.1221333, 53.3159544, 883.925596), (0.1, 600, 4, -16991.6697, 12.7721090, 52.7644553, 471.762394),
      (0.5, 500, 32, -12109.5369, 21.3208159, 58.0077346, 830.295833), (0.5, 500, 1, -18281.3020, 3.6423080, 36.8228098, 510.258362),
      (0.9, 400, 30, -6986.4869, 22.2830797, 51.8072415, 895.748711), (0.9, 400, 0.5, -13790.6278, 1.5499708, 32.9703870, 478.608147))
T7 = ((0.2, 300, 0.040710, 0.9360, 51.941, 0.01640), (0.4, 400, 2.5545, 0.9363, 43.318, 0.8608), (0.6, 500, 16.698, 0.7844, 25.459, 8.86))  # x_L, T, p_BUB, x_v, rho_L, rho_v
T8 = ((0.2, 300, 0.00437062, 0.010672, 55.16434, 0.00175506), (0.4, 400, 0.394694, 0.051541, 50.83187, 0.122658), (0.6, 500, 6.52607, 0.22135, 39.93714, 2.00730))  # x_v, T, p_DEW, x_L, rho_L, rho_v
# Criterios fijados en TASK_CONTEXT_iapws_g4: (modo, tol); no cambiar.
TOL = {("6", "p"): ("rel", 1e-6), ("6", "Cv"): ("rel", 1e-4), ("6", "w"): ("rel", 1e-4), ("6", "f"): ("rel", 1e-6),
       ("7", "p_BUB"): ("rel", 1e-3), ("7", "x_v"): ("abs", 1e-3), ("7", "rho_L"): ("rel", 1e-3), ("7", "rho_v"): ("rel", 1e-3),
       ("8", "p_DEW"): ("rel", 1e-3), ("8", "x_L"): ("abs", 1e-3), ("8", "rho_L"): ("rel", 1e-3), ("8", "rho_v"): ("rel", 1e-3)}

def _t6(motor, p):
    """Tabla 6, punto p -> {propiedad: valor}. teqp: G4-01 Tabla 4 en la convención de teqp."""
    x, T, rho = p[0], p[1], p[2]
    if motor == "iapws":
        r = ng.prop(rho, T, x)
        Mm = ng.Mm(x)  # cv[kJ/kgK]*Mm = J/molK; a[kJ/kg]*Mm = J/mol; w ya m/s
        return {"p": r["P"], "Cv": r["cv"] * Mm, "w": r["w"], "f": r["a"] * Mm}
    z, rs = np.array([x, 1.0 - x]), rho * 1000.0
    aig, M = te._ideal_helmholtz(), te._MODEL
    a20, i20 = M.get_Ar20(T, rs, z), aig.get_Aig20(T, rs, z)
    a01, a02, a11 = M.get_Ar01(T, rs, z), M.get_Ar02(T, rs, z), M.get_Ar11(T, rs, z)
    w2 = (te.R * T / (te.Mm(x) / 1000.0)) * (1 + 2 * a01 + a02 - (1 + a01 - a11) ** 2 / (a20 + i20))
    return {"p": te.P_total(T, z * rs) / 1e6,
            "f": te.R * T * (aig.get_Aig00(T, rs, z) + M.get_Ar00(T, rs, z)),
            "Cv": -te.R * (a20 + i20), "w": w2 ** 0.5}

def _t78(motor, p, kind):
    """Tabla 7 ('bub') u 8 ('dew') -> (vals, est, det)."""
    z, T, bub = p[0], p[1], kind == "bub"
    ks = ("p_BUB", "x_v") if bub else ("p_DEW", "x_L")
    fn = (ng.bubbleP if bub else ng.dewP) if motor == "iapws" else (tf.bubbleP if bub else tf.dewP)
    if motor == "iapws":
        Pm, y, ok = fn(T, z)  # MPa
    else:
        Pp, y, ok = fn(T, z)  # Pa
        Pm = Pp / 1e6
    vals = {ks[0]: Pm, ks[1]: y, "rho_L": None, "rho_v": None}
    if not ok:
        msg = f"flash devolvió ok=False: P={Pm:.8g} MPa, y={y:.8g}"
        return vals, {k: "no_converge" for k in vals}, {k: msg for k in vals}
    if motor == "iapws":
        rL, rV = ng.rho_TPx(T, Pm, z if bub else y, "l"), ng.rho_TPx(T, Pm, y if bub else z, "v")
    else:
        rL, rV = te.rho_liquido(T, Pp, z if bub else y) / 1000.0, te.rho_vapor(T, Pp, y if bub else z) / 1000.0
    vals.update(rho_L=rL, rho_v=rV)
    if abs(y - z) < 1e-6 and abs(rL - rV) <= 1e-4 * abs(rL):
        msg = (f"flash devolvió ok=True pero en raíz degenerada (y={y:.8g}=entrada, "
               f"rho_L={rL:.8g}=rho_v={rV:.8g} mol/dm3): punto en el lugar crítico del "
               f"modelo; P={Pm:.8g} MPa vs {p[2]} de la guía")
        return vals, {k: "no_converge" for k in vals}, {k: msg for k in vals}
    return vals, {k: "evaluar" for k in vals}, {k: "" for k in vals}

def _punto(tabla, i, p):
    return (f"x{p[0]}_T{p[1]}_rho{p[2]}" if tabla == "6"
            else f"x{'L' if tabla == '7' else 'V'}{p[0]}_T{p[1]}")

def _eval_punto(motor, tabla, punto, p, kind):
    if tabla == "6":
        G = (("p", p[4]), ("Cv", p[5]), ("w", p[6]), ("f", p[3]))
    else:
        ks = ("p_BUB", "x_v", "rho_L", "rho_v") if tabla == "7" else ("p_DEW", "x_L", "rho_L", "rho_v")
        G = tuple(zip(ks, p[2:6]))
    g = lambda v: f"{v:.12g}" if isinstance(v, float) else str(v)  # noqa: E731
    try:
        if kind is None:
            vals = _t6(motor, p)
            est = {k: "evaluar" for k, _ in G}; det = dict.fromkeys(est, "")
            if motor == "teqp":
                est["f"] = "esperado_offset"
                det["f"] = ("gas ideal de CoolProp con otro estado de referencia que G4-01 "
                            "(docstring de _teqp_engine.py): offset esperado, en J/mol, no es fallo")
        else:
            vals, est, det = _t78(motor, p, kind)
    except Exception as exc:
        msg = f"{type(exc).__name__}: {exc}"
        vals, est, det = {}, {}, {}
        for k, _ in G:
            vals[k], est[k], det[k] = None, "no_converge", msg
    filas = []
    for k, guia in G:
        modo, tol = TOL[(tabla, k)]
        f = dict(motor=motor, tabla=tabla, punto=punto, propiedad=k, valor_guia=g(guia),
                 valor_motor="", error_abs="", error_rel="", tolerancia=f"{modo}<{tol:.0e}",
                 cumple=est[k], detalle=det[k])
        v = vals.get(k)
        if v is not None:
            ea, er = abs(v - guia), abs(v - guia) / abs(guia)
            f.update(valor_motor=g(v), error_abs=g(ea), error_rel=g(er))
            if est[k] == "evaluar":
                f["cumple"] = "sí" if (ea < tol if modo == "abs" else er < tol) else "no"
            elif est[k] == "esperado_offset":
                f["tolerancia"] = "n/a (offset de estado de referencia)"
        elif est[k] == "no_disponible":
            f["valor_motor"] = "no_disponible"
        filas.append(f)
    return filas

def evaluar_todo():
    """Todas las filas CSV: 2 motores x (6+3+3) puntos x 4 propiedades = 96."""
    filas = []
    for m in MOTORES:
        for t, datos, kind in (("6", T6, None), ("7", T7, "bub"), ("8", T8, "dew")):
            for i, p in enumerate(datos, 1):
                filas += _eval_punto(m, t, _punto(t, i, p), p, kind)
    return filas

def claves_puntos():
    """[(motor, tabla, punto)] únicos (24), mismo orden que el CSV."""
    return [(m, t, _punto(t, i, p)) for m in MOTORES
            for t, datos in (("6", T6), ("7", T7), ("8", T8))
            for i, p in enumerate(datos, 1)]

def _reporte(filas):
    grupos, peor = {}, {}
    for f in filas:
        k = (f["motor"], f["tabla"])
        grupos.setdefault(k, dict(sí=0, no=0, no_converge=0, esperado_offset=0))
        grupos[k][f["cumple"]] += 1
        if f["error_rel"]:
            er, ea = float(f["error_rel"]), float(f["error_abs"])
            pk = (f["motor"], f["propiedad"])
            if pk not in peor or er > peor[pk][0]:
                peor[pk] = (er, ea, f["punto"])
    nom = {"iapws": "motor de referencia `_nh3h2o_engine.py` (iapws 1.5.5)",
           "teqp": "motor teqp `_teqp_engine.py` + `_teqp_flash.py` (teqp 0.23.2)"}
    L = ["# Reporte — Verificación de los dos motores contra IAPWS G4-01 (Tablas 6–8)",
         "Fecha: 2026-09-23 · Tarea `2026-09-23-verificacion-iapws-g4` · solo lectura de `src/`.",
         "Guía: **IAPWS G4-01**, §8, Tablas 6–8 (valores transcritos literalmente); Tillner-Roth & Friend, "
         "*J. Phys. Chem. Ref. Data* **27**, 63 (1998). `x` = molar NH3.",
         "Criterios (fijados en TASK_CONTEXT, no modificados): Tabla 6 p rel<1e-6; Cv,w rel<1e-4; f rel<1e-6 "
         "solo motor referencia (teqp: offset esperado, en J/mol); Tablas 7–8 p,ρ rel<1e-3; x abs<1e-3.",
         "", "## Resumen por motor y tabla",
         "| Motor | Tabla | Filas | sí | no | no_converge | esperado_offset |", "|---|---|---|---|---|---|---|"]
    for (m, t), c in sorted(grupos.items()):
        L.append(f"| {m} | {t} | {sum(c.values())} | {c['sí']} | {c['no']} | {c['no_converge']} | {c['esperado_offset']} |")
    L += ["", "## Peor error por propiedad",
          "| Motor | Propiedad | Peor error rel | Peor error abs | Punto |", "|---|---|---|---|---|"]
    for (m, pr), (er, ea, pt) in sorted(peor.items()):
        L.append(f"| {m} | {pr} | {er:.3e} | {ea:.3g} | `{pt}` |")
    L += ["", "## f en teqp: offset esperado (J/mol; no es fallo)",
          "| Punto | f guía [J/mol] | f teqp [J/mol] | Δ [J/mol] |", "|---|---|---|---|"]
    for f in (x for x in filas if x["motor"] == "teqp" and x["propiedad"] == "f"):
        L.append(f"| `{f['punto']}` | {f['valor_guia']} | {f['valor_motor']} | "
                 f"{float(f['valor_motor']) - float(f['valor_guia']):+.2f} |")
    nc = {(f["motor"], f["tabla"], f["punto"]): f["detalle"] for f in filas if f["cumple"] == "no_converge"}
    L += ["", "## Puntos `no_converge` (nunca ocultados)"]
    for (m, t, p), msg in sorted(nc.items()):
        L.append(f"- **{m}, Tabla {t}, `{p}`**: {msg}")
    L += ["", "## Conclusión por motor"]
    for m in MOTORES:
        malas = [f for f in filas if f["motor"] == m and f["cumple"] == "no"]
        n_ok = sum(1 for f in filas if f["motor"] == m and f["cumple"] == "sí")
        n_nc = len({(f["tabla"], f["punto"]) for f in filas if f["motor"] == m and f["cumple"] == "no_converge"})
        porp = {pr: sorted(float(x["error_rel"]) for x in malas if x["propiedad"] == pr) for pr in {x["propiedad"] for x in malas}}
        if malas:
            det = "; ".join(f"{pr}: {len(v)} filas (err_rel {min(v):.1e}–{max(v):.1e})" for pr, v in sorted(porp.items()))
            veredicto = f"**NO reproduce G4-01 dentro de tolerancia**: {len(malas)} filas fuera de criterio ({det})"
        else:
            veredicto = f"**SÍ reproduce G4-01 dentro de tolerancia**: {n_ok} filas evaluables cumplen su criterio"
        L.append(f"- **{nom[m]}** — {veredicto}." +
                 (f" {n_nc} punto(s) `no_converge` (lugar crítico), registrado con su mensaje real." if n_nc else " Sin `no_converge`."))
    L += ["Cita: IAPWS G4-01 (2001); Tillner-Roth & Friend, J. Phys. Chem. Ref. Data 27, 63 (1998)."]
    return L

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    filas = evaluar_todo()
    with CSV_PATH.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS)
        w.writeheader()
        w.writerows(filas)
    lineas = _reporte(filas)
    REP_PATH.write_text("\n".join(lineas), encoding="utf-8")
    print("\n".join(lineas))
    print(f"CSV: {CSV_PATH.relative_to(REPO)} ({len(filas)} filas)")
    print(f"Reporte: {REP_PATH.relative_to(REPO)}")

if __name__ == "__main__":
    main()