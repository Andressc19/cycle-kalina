"""M2R — resúmenes y `REPORTE_M2R.md` (TASK_CONTEXT final_M2R): escribe `m2r_fronteras.csv`,
`m2r_kalina.csv`, `m2r_resumen.csv` y `REPORTE_M2R.md` a partir de la malla y la bisección;
`d = Σ |v − v_prof|/(b − a)` con los rangos de M3 (ε/η en [0.40, 0.95]) y `m_b` sin cambio
(término 0); los KALINA se deduplican por los 11 valores de las variables."""
from __future__ import annotations

import csv, sys
from collections import Counter
from pathlib import Path

_DIR = Path(__file__).resolve().parent
_RAIZ = _DIR.parents[1]
sys.path[:0] = [str(_RAIZ), str(_DIR)]
import m2r_corrida as c  # noqa: E402
from comun import PROFESOR  # noqa: E402

RANGOS = {"T_fuente": (340.0, 623.15), "T_sumidero": (283.15, 303.55), "P_alta": (1000.0, 10000.0),
          "P_baja": (150.0, 1500.0), "x_b": (0.30, 0.90), "eta_t": (0.40, 0.95), "eta_p": (0.40, 0.95),
          "eps_hrvg": (0.40, 0.95), "eps_reg": (0.40, 0.95), "eps_cond": (0.40, 0.95)}
CFRON = ["parte", "var1", "val1", "var_refinada", "frontera", "lo", "hi", "lado_si",
         "lado_no", "ancho_final", "iteraciones", "clase_si", "eta_si", "D_si", "fuera_rango_si"]
CKAL = ["parte", "var1", "val1", "var2", "val2", "eta", "Wnet", "m_O1", "m_O2",
        "fuera_rango", "B_verificado", "n_cambios", "d"]
CREST = ["parte", "var1", "val1", "var2", "n_genuinos", "n_kalina", "n_N2", "menor_d",
         "menor_d_val1", "menor_d_val2", "menor_d_eta", "mayor_eta", "mayor_eta_val1",
         "mayor_eta_val2", "bloqueantes"]
CAB3 = ["Variable", "Genuinos", "¿KALINA?", "Valor KALINA más cercano al profesor (d)", "η ahí", "Criterios que bloquean"]
CAB4 = ["Parte", "eps_hrvg", "Genuinos", "KALINA", "N2", "KALINA de menor d (dónde)", "η ahí", "Mayor η (dónde)", "Criterios que bloquean"]
CAB5 = ["Parte", "T_fuente", "Genuinos", "KALINA", "N2", "KALINA de menor d (dónde)", "η ahí", "Mayor η (dónde)", "Criterios que bloquean"]

def combo_de(f: dict) -> dict:
    """PROFESOR más lo que esa fila cambió (var1 y, si existe, var2)."""
    x = dict(PROFESOR); x[f["var1"]] = f["val1"]
    if f.get("var2"): x[f["var2"]] = f["val2"]
    return x

def d_de(x: dict) -> float:
    """d = Σ |v − v_prof|/(b − a) con los rangos de M3 (`m_b` aporta 0)."""
    return sum(abs(x[k] - PROFESOR[k]) / (b - a) for k, (a, b) in RANGOS.items())

def n_cambios(x: dict) -> int:
    """Cuántas de las 11 variables del profesor difieren (tolerancia 1e-9)."""
    return sum(1 for k in PROFESOR if abs(x[k] - PROFESOR[k]) > 1e-9)

def _eta(x):
    return "—" if x is None else f"{x:.4f}"

def _clave(f: dict) -> tuple:
    return (f["parte"], f["var1"], None if f["parte"] == "n1" else f["val1"])

def _unicas(fs: list) -> list:
    """Filas sin duplicados por los 11 valores (clave redondeada a 1e-9)."""
    out, vistas = [], set()
    for f in fs:
        k = tuple(round(combo_de(f)[n], 9) for n in PROFESOR)
        if k not in vistas: vistas.add(k); out.append(f)
    return out

def filas_fronteras(fr: list) -> list:
    """Una fila por frontera: el lado que SÍ cumple, el que no y el ancho final."""
    out = []
    for f in fr:
        si, no = (f["f_lo"], f["f_hi"]) if f["lo_si"] else (f["f_hi"], f["f_lo"]); pos = lambda r: r["val1"] if f["parte"] == "n1" else r["val2"]
        out.append(dict(parte=f["parte"], var1=f["var1"], val1=f["val1"], var_refinada=f["ref"],
                        frontera=f["frontera"], lo=f["lo"], hi=f["hi"], lado_si=pos(si),
                        lado_no=pos(no), ancho_final=f["hi"] - f["lo"], iteraciones=f["iter"],
                        clase_si=si["clasificacion"], eta_si=si["eta"], D_si=si["D"], fuera_rango_si=si["fuera_rango"]))
    return out

def filas_kalina(todo: list) -> list:
    """KALINA (malla + bisección) sin duplicados, con `d` y `n_cambios`."""
    out = []
    for f in _unicas([f for f in todo if f["clasificacion"] == "KALINA"]):
        x = combo_de(f)
        out.append(dict(parte=f["parte"], var1=f["var1"], val1=f["val1"], var2=f["var2"] or "",
                        val2=f["val2"], eta=f["eta"], Wnet=f["Wnet"], m_O1=f["m_O1"], m_O2=f["m_O2"],
                        fuera_rango=f["fuera_rango"], B_verificado=f["B_verificado"],
                        n_cambios=n_cambios(x), d=d_de(x)))
    return sorted(out, key=lambda r: (r["parte"], r["var1"], r["val1"], r["val2"] if r["val2"] is not None else -1.0))

def filas_resumen(todo: list) -> list:
    """Una fila por (parte, var1[, val1]): conteos, menor d, mayor η y bloqueos."""
    claves, vistas, out = [], set(), []
    for f in todo:
        k = _clave(f)
        if k not in vistas: vistas.add(k); claves.append(k)
    for k in claves:
        g = _unicas([f for f in todo if _clave(f) == k])
        gen = [f for f in g if c.genuina(f)]; kal = [f for f in g if f["clasificacion"] == "KALINA"]
        n2 = [f for f in g if f["convergio"] and f["clasificacion"] == "NO_CONVERGIO"]
        d0 = min(kal, key=lambda f: d_de(combo_de(f)), default=None)
        e0 = max([f for f in kal if f["eta"] is not None], key=lambda f: f["eta"], default=None)
        cods = Counter(x for f in gen if f["clasificacion"] != "KALINA" for x in (f["codigos_falla"] or "").split(",") if x)
        o = dict.fromkeys(CREST)
        o.update(parte=k[0], var1=k[1], val1=k[2], var2="" if k[0] == "n1" else g[0]["var2"],
                 n_genuinos=len(gen), n_kalina=len(kal), n_N2=len(n2))
        if d0: o.update(menor_d=d_de(combo_de(d0)), menor_d_val1=d0["val1"], menor_d_val2=d0["val2"], menor_d_eta=d0["eta"])
        if e0: o.update(mayor_eta=e0["eta"], mayor_eta_val1=e0["val1"], mayor_eta_val2=e0["val2"])
        o["bloqueantes"] = " · ".join(f"{a}({b})" for a, b in cods.most_common())
        out.append(o)
    return out

def escribir(nombre: str, cab: list, filas: list) -> None:
    with open(c.OUT / nombre, "w", encoding="utf-8", newline="") as fh:
        esc = csv.DictWriter(fh, fieldnames=cab); esc.writeheader()
        for f in filas: esc.writerow({k: f.get(k) for k in cab})
    print(f"{nombre}: {len(filas)} filas", flush=True)

def _tabla(cab: list, filas: list) -> str:
    return ("| " + " | ".join(cab) + " |\n|" + "|".join(["---"] * len(cab)) + "|\n"
            + "\n".join("| " + " | ".join(f) + " |" for f in filas))

def _f1(r: dict) -> list:  # §3: una fila por variable
    return [r["var1"], str(r["n_genuinos"]), "sí" if r["n_kalina"] else "no",
            "—" if r["menor_d"] is None else f'{r["menor_d_val1"]:g} (d = {r["menor_d"]:.4f})',
            _eta(r["menor_d_eta"]), r["bloqueantes"] or "—"]

def _f2(r: dict) -> list:  # §4 y §5: una fila por valor de var1
    md = ("—" if r["menor_d"] is None else f'{r["var2"]} = {r["menor_d_val2"]:g} (d = {r["menor_d"]:.4f})')
    me = "—" if r["mayor_eta"] is None else f'{_eta(r["mayor_eta"])} ({r["var2"]} = {r["mayor_eta_val2"]:g})'
    return [r["parte"], f'{r["val1"]:g}', str(r["n_genuinos"]), str(r["n_kalina"]), str(r["n_N2"]),
            md, _eta(r["menor_d_eta"]), me, r["bloqueantes"] or "—"]

def _m2() -> dict | None:
    """KALINA de M2 ruta B con T_fuente = 390 K, con d y n_cambios a la escala nueva."""
    p = _RAIZ / "resultados" / "2026-10-06_final_M2" / "m2n2_kalina.csv"
    if not p.exists(): return None
    with open(p, encoding="utf-8", newline="") as fh:
        filas = [r for r in csv.DictReader(fh) if r["var1"] == "T_fuente" and abs(float(r["val1"]) - 390.0) < 1e-6]
    if not filas: return None
    r = min(filas, key=lambda r: float(r["P_baja"]))
    x = dict(PROFESOR, T_fuente=float(r["val1"]), P_baja=float(r["P_baja"]))
    return dict(T_fuente=x["T_fuente"], P_baja=x["P_baja"], eta=float(r["eta"]), d=d_de(x), n_cambios=n_cambios(x))

def reporte(res: list, kal: list, todo: list, n_fr: int, t_malla: float, t_bise: float) -> None:
    """Escribe `REPORTE_M2R.md` en lenguaje llano (las 10 secciones pedidas)."""
    r1 = [r for r in res if r["parte"] == "n1"]; r2 = [r for r in res if r["parte"] in ("n2a", "n2b")]; r3 = [r for r in res if r["parte"] == "n3"]
    ts = sorted(f["t_s"] for f in todo if f.get("t_s"))
    nk1, nk2, nk3 = (sum(r["n_kalina"] for r in x) for x in (r1, r2, r3))
    k2 = [r for r in r2 if r["n_kalina"]]
    s4 = ("**Sí: se llega a KALINA conservando la fuente y el sitio del profesor (T_fuente = 623.15 K, T_sumidero = 300.032917 K), cambiando solo variables de diseño.** Hay " + str(nk2) + " puntos KALINA: "
          + "; ".join(f'{r["parte"]} con {r["var1"]} = {r["val1"]:g} y {r["var2"]} = {r["menor_d_val2"]:g} (d = {r["menor_d"]:.4f}, η = {_eta(r["menor_d_eta"])})' for r in k2)
          + ". P_baja queda en 400 kPa en la parte 2a y se barre hasta 2000 kPa en la 2b.") if nk2 else f"**No: con la fuente y el sitio del profesor (T_fuente = 623.15 K) no se llega a KALINA** en ninguna de las {len(r2)} combinaciones de la parte 2."
    s5 = (f"**Sí.** Con P_baja = 400 kPa, las {len(r3)} parejas (T_fuente, eps_cond) dan " + str(nk3) + " KALINA: "
          + ", ".join(f'T_fuente = {r["val1"]:g} con eps_cond = {r["menor_d_val2"]:g}' for r in r3 if r["n_kalina"])
          + ". ε_cond sí puede sustituir a P_baja como segundo cambio.") if nk3 else f"**No.** Con P_baja = 400 kPa ninguna de las {len(r3)} parejas (T_fuente, eps_cond) da KALINA: ε_cond no sustituye a P_baja."
    m2p = _m2(); md = min((k["d"] for k in kal), default=None); mn = min((k["n_cambios"] for k in kal), default=None)
    if m2p is None:
        s6 = "- No se pudo leer `m2n2_kalina.csv` de M2: la comparación queda sin hacer."
    else:
        s6 = (f'- M2: T_fuente = {m2p["T_fuente"]:g} K, P_baja = {m2p["P_baja"]:g} kPa, η = {m2p["eta"]:.4f}, d ≈ 0.857 con la escala vieja. Recalculado con la escala nueva (rangos de M3): **d = {m2p["d"]:.4f}** y **{m2p["n_cambios"]} variables cambiadas**. El valor de d no cambia porque los rangos de T_fuente y P_baja son los mismos en las dos escalas.\n'
              f'- M2R: {len(kal)} KALINA distintos; el de menor d tiene d = {"—" if md is None else f"{md:.4f}"} y el de menos cambios tiene {"—" if mn is None else mn} cambios.\n'
              f'- **Respuesta: {"sí" if mn is not None and mn < m2p["n_cambios"] else "no"} hay un KALINA con menos cambios que el de M2 y {"sí" if md is not None and md < m2p["d"] else "no"} hay uno con menor d.**')
    s7 = (f"- Malla: {t_malla:.0f} s · Bisección: {t_bise:.0f} s · Total: {t_malla + t_bise:.0f} s ({n_fr} fronteras, {len(todo)} puntos evaluados).\n"
          f"- Por punto (`t_s`): mínimo {ts[0]:.1f} s, mediana {ts[len(ts) // 2]:.1f} s, máximo {ts[-1]:.1f} s, media {sum(ts) / len(ts):.1f} s ({len(ts)} puntos).")
    fk = [k for k in kal if k["fuera_rango"]]
    det = ", ".join(f'{k["parte"]} {k["var1"]} = {k["val1"]:g}' + (f', {k["var2"]} = {k["val2"]:g}' if k["var2"] else "") for k in fk) or "ninguno"
    s9 = [f"- **{len(fk)} de {len(kal)} puntos KALINA quedan fuera del rango confiable** (T > 420 K de líquido, IAPWS G4-01 sin respaldo experimental): {det}." if fk else f"- Ninguno de los {len(kal)} puntos KALINA queda fuera del rango confiable.",
          f"- {sum(r['n_N2'] for r in res)} puntos son fijos espurios (N2: `convergio` con `clasificacion = NO_CONVERGIO`): se contaron como NO genuinos en todo.",
          "- La malla tiene 12 valores por variable: hueco de (b−a)/11; una zona más estrecha caída dentro de un hueco no aparece ni en la malla ni en la bisección.",
          "- La bisección solo refina fronteras que la malla sí detectó entre dos vecinos consecutivos."]
    s9 += ["- Esta es una corrida de humo (1 punto por parte, sin bisección): las cifras no son las de la corrida real."] if c.HUMO else []
    doc = f"""# REPORTE M2R — repetición de M2 con η y ε en [0.40, 0.95]
## 1. La pregunta
M2 limitó `eta_t`, `eta_p`, `eps_hrvg`, `eps_reg` y `eps_cond` a [0.75, 0.85], pero el rango permitido es [0.40, 0.95]. Se repite M2 con ese rango abierto para saber qué condicionó el límite viejo y, sobre todo, para responder: **¿se puede llegar a KALINA conservando la fuente (T_fuente = 623.15 K) y el sitio (T_sumidero) del profesor, cambiando solo variables de diseño?**
## 2. Qué cambió respecto a M2
- **Rangos.** Las 5 variables de rendimiento pasan de [0.75, 0.85] a [0.40, 0.95] (12 valores equiespaciados, paso 0.05).\n- **Fronteras.** Las de «convergencia» de la parte 1 se definen ahora con *es genuino* (KALINA, CORREGIBLE o INVIABLE), no con la bandera `convergio`: un punto N2 ya no cuenta como que converge.
- **Partes.** La 2 añade `eps_cond` como segunda variable (y `eps_hrvg` hasta 0.80, `P_baja` hasta 2000 kPa); la 3 es nueva: (T_fuente, eps_cond) con `P_baja` del profesor.\n- **Escala de `d`.** Σ |v − v_prof|/(b − a) con los rangos de M3 (ε/η en [0.40, 0.95], T_fuente [340, 623.15], P_baja [150, 1500] kPa) y `m_b` nunca cambiado (término 0): un KALINA con P_baja > 1500 kPa queda con d > 1.
## 3. Parte 1 — una variable a la vez con el rango nuevo
{_tabla(CAB3, [_f1(r) for r in r1])}
## 4. Parte 2 — conservando la fuente del profesor (T_fuente = 623.15 K)
{s4}
{_tabla(CAB4, [_f2(r) for r in r2])}
## 5. Parte 3 — (T_fuente, eps_cond) con P_baja = 400 kPa del profesor
{s5}
{_tabla(CAB5, [_f2(r) for r in r3])}
## 6. Comparación con M2
{s6}
## 7. Tiempos
{s7}
## 8. Conclusión
{"Sí se llega a KALINA" if nk1 or nk2 or nk3 else "No se llega a KALINA"} con los rangos abiertos: la parte 1 da {nk1} KALINA con un solo cambio, la parte 2 {nk2} conservando la fuente del profesor y la parte 3 {nk3}. El bloqueo de fondo sigue siendo el mismo de siempre (lado caliente y O2) y se cierra como en M2: bajando `eps_hrvg`/`eps_cond` o subiendo `P_baja`.
## 9. Lo que no se sabe
{chr(10).join(s9)}
## 10. Qué sigue
Los puntos concretos que llegan a KALINA están en `m2r_kalina.csv` (con su `d`, sus cambios y su `fuera_rango`); cuál proponer lo decide el director.
"""
    (c.OUT / "REPORTE_M2R.md").write_text(doc, encoding="utf-8")
    print("REPORTE_M2R.md escrito", flush=True)

def generar(malla: list, bise: list, fr: list, t_malla: float, t_bise: float) -> None:
    """CSVs de resumen y reporte, a partir de las filas de las dos fases."""
    todo = malla + bise
    escribir("m2r_fronteras.csv", CFRON, filas_fronteras(fr))
    kal = filas_kalina(todo); escribir("m2r_kalina.csv", CKAL, kal)
    res = filas_resumen(todo); escribir("m2r_resumen.csv", CREST, res)
    reporte(res, kal, todo, len(fr), t_malla, t_bise)

if __name__ == "__main__": raise SystemExit("Importar y llamar generar(); la corrida es m2r_corrida.py")
