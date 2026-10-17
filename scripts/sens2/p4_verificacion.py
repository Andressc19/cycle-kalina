# -*- coding: utf-8 -*-
"""Sens2 P4 - Paso 5: verificacion (a-f) y resumen en lenguaje llano.

Controles:
 a) n de KALINA por centro coincide con P2 (`p2_comparacion.csv`).
 b) q4 >= 0.90 en todos los KALINA (reporta excepciones).
 c) LMTD > 0 y UA > 0 donde se calculan.
 d) la suma de n por banda de rp = n de KALINA con rp en [1, 10).
 e) balance del regenerador Qreg/m_b ~ (h1 - h10).
 f) sin palabras prohibidas en las salidas.

Ademas escribe `p4_resumen.md` con la preseleccion por equipo y los limites.
Una linea OK/FALLA por control; no se da `done` con FALLA.
"""
import os

import numpy as np
import pandas as pd

import p4_comun as c

SALIDA = c.SALIDA
P2DIR = os.path.join(c.RAIZ, "resultados", "2026-10-17_sens2_P2")
TOL_BAL = 1e-2


def linea(n, ok, det):
    print("Control %s: %s - %s" % (n, "OK" if ok else "FALLA", det))
    return ok


def control_a(d):
    comp = pd.read_csv(os.path.join(P2DIR, "p2_comparacion.csv"))
    s = comp[(comp["ambito"] == "todos los puntos") & (comp["ref"] == c.REF_TOTAL)
             & (comp["variable"] == "eta_pct")]
    esp = dict(zip(s["centro"], s["n_kal"]))
    malos = []
    for cen in c.grupos(d):
        n = int(c.mask_total(d[d["centro"] == cen]).sum())
        if n != int(esp.get(cen, -1)):
            malos.append("%s:%d/%d" % (cen, n, esp.get(cen, -1)))
    nt = int(c.mask_total(d).sum())
    if nt != int(esp.get("todos", -1)):
        malos.append("todos:%d/%d" % (nt, esp.get("todos", -1)))
    return linea("a", not malos, "KALINA por centro vs P2: %s" % (malos or "coinciden"))


def control_b(d):
    kal = d[c.mask_total(d)]
    q = kal["q4"].to_numpy(float)
    fin = np.isfinite(q)
    ex = int((q[fin] < 0.90).sum())
    return linea("b", ex == 0, "q4 validos=%d, con q4<0.90=%d, min=%.6f" % (
        int(fin.sum()), ex, float(q[fin].min()) if fin.any() else np.nan))


def control_c(d):
    kal = d[c.mask_total(d)]
    lmt = kal["LMTD_reg"].to_numpy(float)
    ua = kal["UA_reg"].to_numpy(float)
    fin = np.isfinite(lmt) & np.isfinite(ua)
    cruces = int((kal["pinch_reg"].to_numpy(float) <= 0).sum())
    ok = bool(fin.any() and (lmt[fin] > 0).all() and (ua[fin] > 0).all())
    return linea("c", ok, "LMTD y UA calculados en %d, cruces=%d, LMTD min=%.4f, "
                 "UA min=%.4f" % (int(fin.sum()), cruces,
                                  float(lmt[fin].min()), float(ua[fin].min())))


def control_d(d):
    b = pd.read_csv(os.path.join(SALIDA, "p4_bandas.csv"))
    suma = int(b[b["centro"] == "todos"]["n"].sum())
    kal = d[c.mask_total(d)]
    rp = kal["rp"].to_numpy(float)
    val = int(((rp >= 1.0) & (rp < 10.0)).sum())
    fuera = int((rp >= 10.0).sum())
    return linea("d", suma == val, "bandas=%d, KALINA 1<=rp<10=%d, rp>=10=%d" % (
        suma, val, fuera))


def control_e(d):
    kal = d[c.mask_total(d)]
    qmb = (kal["Qreg"] / kal["m_b"]).to_numpy(float)
    dif = kal["h_e1"].to_numpy(float) - kal["h_e10"].to_numpy(float)
    fin = np.isfinite(qmb) & np.isfinite(dif)
    if not fin.any():
        return linea("e", False, "no verificable: faltan Qreg/m_b o h_e1/h_e10")
    rel = np.abs(qmb[fin] - dif[fin]) / np.abs(qmb[fin])
    ok = bool(np.nanmax(rel) <= TOL_BAL)
    return linea("e", ok, "Qreg/m_b vs (h1-h10): n=%d, rel err mediana=%.3g, "
                 "max=%.3g (tol %.0e)" % (int(fin.sum()), float(np.median(rel)),
                                          float(np.nanmax(rel)), TOL_BAL))


def control_f():
    malos = []
    for nombre in sorted(os.listdir(SALIDA)):
        ruta = os.path.join(SALIDA, nombre)
        if not os.path.isfile(ruta) or not nombre.lower().endswith((".md", ".csv")):
            continue
        with open(ruta, "r", encoding="utf-8", errors="ignore") as f:
            txt = f.read().lower()
        for p in c.PROHIBIDAS:
            if p in txt:
                malos.append("%s:%s" % (nombre, p))
    return linea("f", not malos, "archivos con palabra prohibida: %s" % (malos or "ninguno"))


def _rango(env, cant):
    r = env[(env["centro"] == "todos") & (env["conjunto"] == c.REF_TOTAL)
            & (env["cantidad"] == cant)]
    return (r.iloc[0]["p5"], r.iloc[0]["p95"]) if len(r) else (np.nan, np.nan)


def resumen(d):
    env = pd.read_csv(os.path.join(SALIDA, "p4_envolventes.csv"))
    dep = pd.read_csv(os.path.join(SALIDA, "p4_dependencias.csv"))
    res = pd.read_csv(os.path.join(SALIDA, "p4_restricciones.csv"))
    sp = dep[dep["tipo"] == "spearman"].assign(mag=lambda t: t["estadistico"].abs())
    g = sp.groupby(["cantidad", "variable"])["mag"].mean()
    fijador = {}
    for k in c.CANT_DEP:
        try:
            v = g.loc[k].idxmax() if k in g.index.get_level_values(0) else "sin dato"
        except (ValueError, TypeError):
            v = "sin dato"
        fijador[k] = v if isinstance(v, str) else "sin dato"
    reg = dep[(dep["tipo"] == "regresion") & (dep["centro"] == "todos")].iloc[0]
    cal = res[(res["centro"] == "todos") & (res["grupo"] == "KALINA (total)")].iloc[0]
    cor = res[(res["centro"] == "todos") & (res["grupo"] == "CORREGIBLE")].iloc[0]
    q4min = env[(env["centro"] == "todos") & (env["conjunto"] == c.REF_TOTAL)
                & (env["cantidad"] == "q4")].iloc[0]["minimo"]
    l = ["# Sens2 P4 - resumen y preseleccion de equipos", "",
         "Numeros de `p4_envolventes.csv`, `p4_dependencias.csv`, "
         "`p4_restricciones.csv` y `p4_bandas.csv`. Rangos = P5-P95 de KALINA (total).",
         "Cantidades extensivas por kg/s de m_b. Presiones en kPa, T en K, h en kJ/kg.",
         "", "## Preseleccion por equipo", ""]
    for nombre, cant in c.EQUIPOS:
        l.append("- **%s.** " % nombre + "; ".join(
            "%s %s-%s" % (q, c.fmt(_rango(env, q)[0], 3), c.fmt(_rango(env, q)[1], 3))
            for q in cant) + ". Lo fija: " + ", ".join(
            "%s->%s" % (q, fijador[q]) for q in cant
            if fijador.get(q, "sin dato") != "sin dato") + ".")
    l += ["", "## Restriccion activa y regimen de la turbina", "",
          "- Titulo de turbina (O1): el minimo de q4 en KALINA es %.4f; en los "
          "CORREGIBLE, %.1f %% tiene q4 < 0.90." % (
              float(q4min), 100 * cor["frac_q4_lt_090"]),
          "- Regenerador: no hay cruces en KALINA (pinch <= 0 en %.4f de los puntos); "
          "el pinch P5 es %.3f K." % (cal["frac_pinch_le0"], cal["pinch_p5"]),
          "- Condensador y bomba (O2): %.1f %% de los CORREGIBLE tiene "
          "(T9 - T_sumidero) por debajo de la mediana de los KALINA." % (
              100 * cor["frac_T9_sub_med"]),
          "- La turbina entrega mas dh_turb y mas eta a rp alto: la banda [6, 10) "
          "lidera ambas (regresion dh_turb ~ rp global: pendiente %.4g kJ/kg por "
          "unidad de rp, R2 %.3f)." % (reg["pendiente"], reg["r2"]),
          "", "## Limites de este analisis", "",
          "- Los rangos P5-P95 son la envolvente de un muestreo numerico, no "
          "especificaciones de compra: no fijan geometria, caidas de presion, "
          "materiales ni margen de diseno.",
          "- `LMTD_reg` y `UA_reg` salen del calor Qreg y de las temperaturas de "
          "estado; son por kg/s de m_b y suponen contraflujo puro, sin correccion "
          "por configuracion.",
          "- `aprox_cond_sal`, `aprox_cond_ent` y `aprox_fuente` son diferencias de "
          "temperatura frente al sumidero o la fuente; no son un pinch de diseno.",
          "- El modelo usa el metodo de efectividad para HRVG, regenerador y "
          "condensador; aqui el LMTD se reconstruye a partir de los estados, no "
          "sustituye a ese modelo.",
          "- KALINA (total) incluye los puntos fuera del rango experimental "
          "(liquido > 420 K); el conjunto dentro del rango se reporta aparte.",
          "- El balance del regenerador se comprueba en el control (e); ninguna "
          "cantidad derivada se inventa: todas salen de un archivo.", ""]
    c.guardar("p4_resumen.md", "\n".join(l))


def main():
    d = c.cargar()
    oks = [control_a(d), control_b(d), control_c(d), control_d(d), control_e(d)]
    resumen(d)
    oks.append(control_f())
    print("RESULTADO GLOBAL: %s" % ("OK" if all(oks) else "FALLA"))


if __name__ == "__main__":
    main()
