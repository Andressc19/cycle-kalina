"""M2 nivel 2 — resúmenes y `REPORTE_M2_N2.md` (TASK_CONTEXT final_M2_N2).
Escribe `m2n2_fronteras.csv`, `m2n2_kalina.csv`, `m2n2_resumen.csv` y `REPORTE_M2_N2.md` a partir de las filas de la malla y de la bisección que le entrega `m2_nivel2.py::generar`. El índice `d` usa los rangos del nivel 1: eps_hrvg [0.75, 0.85], T_fuente [340, 623.15] y P_baja [150, 1500], aunque la malla de este nivel llegue a 2000 kPa."""
from __future__ import annotations

import csv, sys
from collections import Counter
from pathlib import Path

_DIR = Path(__file__).resolve().parent
_RAIZ = _DIR.parents[1]
sys.path[:0] = [str(_RAIZ), str(_DIR)]

import m2_nivel2 as n2  # noqa: E402
from comun import PROFESOR  # noqa: E402

CFRON = ["ruta", "var1", "val1", "frontera", "P_baja_si", "P_baja_no", "ancho_final", "iteraciones", "clase_si", "eta_si", "D_si", "fuera_rango_si", "codigos_falla_si"]
CKAL = ["ruta", "var1", "val1", "P_baja", "eta", "Wnet", "m_O1", "m_O2", "d", "fuera_rango", "detalle_rango", "B_verificado"]
CREST = ["ruta", "var1", "val1", "n_genuinos", "n_kalina", "n_espurios_N2", "P_baja_min_kalina", "eta_min_kalina", "fuera_rango_min_kalina", "P_baja_min_O2", "mejor_D", "P_baja_mejor_D", "criterios_bloqueantes_frecuentes"]
RANGOS = {"eps_hrvg": (0.75, 0.85), "T_fuente": (340.0, 623.15)}
P_A, P_B, P_PROF = 150.0, 1500.0, PROFESOR["P_baja"]   # escala de `d` del nivel 1: P_baja en [150, 1500], referencia 400 kPa
RUTA_A = "Ruta A — solo diseño (eps_hrvg con la fuente y el sitio del profesor)"
RUTA_B = "Ruta B — sitio + diseño (T_fuente con todo lo demás del profesor)"


def bloqueos(filas: list) -> Counter:
    """Códigos de los puntos GENUINOS que no son KALINA (los espurios N2, no)."""
    return Counter(x for f in filas if n2.genuina(f)
                   and f["clasificacion"] != "KALINA"
                   for x in (f["codigos_falla"] or "").split(",") if x)


def filas_fronteras(fr: list) -> list:
    """Una fila por frontera: el lado que SÍ cumple y el que NO, con su clase."""
    out = []
    for f in fr:
        si, no = (f["f_lo"], f["f_hi"]) if f["lo_si"] else (f["f_hi"], f["f_lo"])
        out.append(dict(ruta=f["ruta"], var1=f["var1"], val1=f["val1"], frontera=f["frontera"],
                        P_baja_si=si["P_baja_val"], P_baja_no=no["P_baja_val"], ancho_final=f["hi"] - f["lo"],
                        iteraciones=f["iter"], clase_si=si["clasificacion"], eta_si=si["eta"],
                        D_si=si["D"], fuera_rango_si=si["fuera_rango"], codigos_falla_si=si["codigos_falla"]))
    return sorted(out, key=lambda r: (r["ruta"], r["val1"], r["P_baja_si"], r["frontera"]))


def filas_kalina(todo: list) -> list:
    """Todas las filas KALINA (malla + bisección) con su índice de cercanía `d`."""
    out = []
    for f in todo:
        if f["clasificacion"] != "KALINA":
            continue
        a, b = RANGOS[f["var1"]]
        d = abs(f["val1"] - PROFESOR[f["var1"]]) / (b - a) + abs(f["P_baja"] - P_PROF) / (P_B - P_A)
        out.append(dict(ruta=f["ruta"], var1=f["var1"], val1=f["val1"], P_baja=f["P_baja"],
                        eta=f["eta"], Wnet=f["Wnet"], m_O1=f["m_O1"], m_O2=f["m_O2"], d=d,
                        fuera_rango=f["fuera_rango"], detalle_rango=f["detalle_rango"],
                        B_verificado=f["B_verificado"]))
    return sorted(out, key=lambda r: (r["ruta"], r["val1"], r["P_baja"]))


def filas_resumen(todo: list) -> list:
    """Una fila por (ruta, val1): conteos, mínimos y bloqueantes."""
    out = []
    for ruta, (var1, vals) in n2.RUTAS.items():
        for val1 in vals:
            g = [f for f in todo if f["ruta"] == ruta and f["val1"] == val1]
            gen = [f for f in g if n2.genuina(f)]
            kal = sorted([f for f in g if n2.es_kalina(f)], key=lambda f: f["P_baja"])
            esp = sum(1 for f in g if f["convergio"] and f["clasificacion"] == "NO_CONVERGIO")
            o2 = [f["P_baja"] for f in gen if f["m_O2"] is not None and f["m_O2"] >= 0.0]
            conD = sorted([f for f in g if f["D"] is not None], key=lambda f: (f["D"], f["P_baja"]))
            k0, d0 = (kal[0] if kal else None), (conD[0] if conD else None)
            out.append(dict(ruta=ruta, var1=var1, val1=val1, n_genuinos=len(gen),
                            n_kalina=len(kal), n_espurios_N2=esp,
                            P_baja_min_kalina=k0["P_baja"] if k0 else None,
                            eta_min_kalina=k0["eta"] if k0 else None,
                            fuera_rango_min_kalina=k0["fuera_rango"] if k0 else None,
                            P_baja_min_O2=min(o2) if o2 else None,
                            mejor_D=d0["D"] if d0 else None, P_baja_mejor_D=d0["P_baja"] if d0 else None,
                            criterios_bloqueantes_frecuentes=" · ".join(
                                f"{k}({n})" for k, n in bloqueos(g).most_common())))
    return out


def escribir(nombre: str, cab: list, filas: list) -> None:
    with open(n2.OUT / nombre, "w", encoding="utf-8", newline="") as fh:
        esc = csv.DictWriter(fh, fieldnames=cab); esc.writeheader()
        for f in filas:
            esc.writerow({c: f.get(c) for c in cab})
    print(f"{nombre}: {len(filas)} filas", flush=True)


def _tabla_ruta(ruta: str, res: list) -> str:
    """Sección §3 de una ruta: una fila por val1."""
    var1 = n2.RUTAS[ruta][0]
    filas = []
    for r in (x for x in res if x["ruta"] == ruta):
        if r["n_kalina"]:
            pb, et = f'{r["P_baja_min_kalina"]:g}', f'{r["eta_min_kalina"]:.4f}'
            fu, bloq = ("sí" if r["fuera_rango_min_kalina"] else "no"), "—"
        else:
            pb = et = fu = "—"
            bloq = r["criterios_bloqueantes_frecuentes"] or "—"
        filas.append(f'| {r["val1"]:g} | {"sí" if r["n_kalina"] else "no"} | {pb} | {et} | {fu} | {bloq} |')
    return (f"### {RUTA_A if ruta == 'A' else RUTA_B}\n\n| {var1} | ¿Hay KALINA? | Menor P_baja KALINA (kPa) | η en ese punto | Fuera de rango | Qué bloquea si no hay KALINA |\n|---|---|---|---|---|---|\n" + "\n".join(filas))


def _tabla_kalina(kal: list) -> str:
    """Sección §4: el KALINA de menor d y el de mayor η de cada ruta."""
    filas = []
    for ruta in n2.RUTAS:
        ks = [k for k in kal if k["ruta"] == ruta]
        con_eta = [k for k in ks if k["eta"] is not None]
        dmin = sorted(ks, key=lambda k: (k["d"], k["P_baja"], k["val1"]))[0] if ks else None
        emax = sorted(con_eta, key=lambda k: (-k["eta"], k["P_baja"], k["val1"]))[0] if con_eta else None
        for criterio, k in (("menor d", dmin), ("mayor η", emax)):
            filas.append(f"| {ruta} | {criterio} | — | — | — | — |" if k is None else
                         f"| {ruta} | {criterio} | {k['val1']:g} | {k['P_baja']:g} | {k['eta']:.4f} | {k['d']:.4f} |")
    return ("| Ruta | Criterio | valor de la variable 1 | P_baja (kPa) | η | d |\n"
            "|---|---|---|---|---|---|\n" + "\n".join(filas))


def _ruta_txt(ruta: str, res: list, todo: list) -> str:
    """Frase de §6 para una ruta."""
    rs = [r for r in res if r["ruta"] == ruta]
    n, var1 = sum(1 for r in rs if r["n_kalina"]), n2.RUTAS[ruta][0]
    if n:
        k = min((r for r in rs if r["n_kalina"]), key=lambda r: r["P_baja_min_kalina"])
        return (f"{n} de {len(rs)} valores de {var1} alcanzan KALINA; la menor P_baja es "
                f'{k["P_baja_min_kalina"]:g} kPa con η = {k["eta_min_kalina"]:.4f}'
                + (" (fuera de rango)" if k["fuera_rango_min_kalina"] else ""))
    cods = bloqueos([f for f in todo if f["ruta"] == ruta])
    gen = sum(1 for f in todo if f["ruta"] == ruta and n2.genuina(f))
    que = f"lo que bloquea es {cods.most_common(1)[0][0]}" if cods else ("la ruta no tiene ni un punto genuino" if not gen else "ningún criterio marcado")
    return f"ninguno de los {len(rs)} valores de {var1} alcanza KALINA; {que}"


def reporte(kal, res, fron, todo, t_malla, t_bise) -> None:
    """Escribe `REPORTE_M2_N2.md` en lenguaje llano (las 8 secciones pedidas)."""
    ts = sorted(f["t_s"] for f in todo if f.get("t_s"))
    n_kal = sum(r["n_kalina"] for r in res)
    fk = [k for k in kal if k["fuera_rango"]]
    grupos = {}
    for k in fk:
        grupos.setdefault((k["ruta"], k["var1"], k["val1"]), []).append(k["P_baja"])
    det = "; ".join(f'Ruta {r} {v}={vv:g}: P_baja {", ".join(f"{p:g}" for p in sorted(ps))}'
                    for (r, v, vv), ps in sorted(grupos.items())) or "ninguno"
    s3 = "\n\n".join(_tabla_ruta(r, res) for r in n2.RUTAS)
    s5 = (f"- Malla: {t_malla:.0f} s · Bisección: {t_bise:.0f} s · Total: {t_malla + t_bise:.0f} s.\n"
          f"- Por punto (`t_s`): mínimo {ts[0]:.1f} s, mediana {ts[len(ts) // 2]:.1f} s, máximo {ts[-1]:.1f} s, media {sum(ts) / len(ts):.1f} s ({len(ts)} puntos).")
    s6 = (f"Con dos cambios {'**sí**' if n_kal else '**no**'} se alcanza KALINA. "
          f"Ruta A (conservando la fuente del profesor): {_ruta_txt('A', res, todo)}. "
          f"Ruta B: {_ruta_txt('B', res, todo)}.")
    s7 = [f"- **{len(fk)} de {len(kal)} puntos KALINA quedan fuera del rango confiable** (T > 420 K de líquido, IAPWS G4-01 sin respaldo experimental): {det}." if fk else
          ("- No se encontró ningún punto KALINA: no hay ninguno fuera del rango confiable (T > 420 K de líquido)." if not kal else
           f"- Ninguno de los {len(kal)} puntos KALINA encontrados queda fuera del rango confiable (T > 420 K de líquido)."),
          "- Los puntos medios de la bisección se evalúan a ciegas y pueden caer en zonas espurias (N2); cuando eso pasa en una frontera O2 se anota `punto medio no genuino` en `m2n2_biseccion.csv` y se toma como el lado que NO cumple.",
          f"- La malla de P_baja tiene solo 12 valores entre 400 y 2000 kPa por valor de la variable 1: el hueco entre vecinos es de {1600 / 11:.1f} kPa; una zona KALINA más estrecha que eso y dentro de un hueco no aparece ni en la malla ni en la bisección."]
    s7 += ["- Esta es una corrida de humo (1 valor por ruta × 2 valores de P_baja, sin bisección): las cifras de arriba no son las de la corrida real."] if n2.HUMO else []
    doc = f"""# REPORTE M2 nivel 2 — ¿con DOS cambios al enunciado del profesor aparece KALINA?
## 1. La pregunta
Se cambian **dos** variables de los datos del profesor —siempre `P_baja`, que es la regla del proyecto para cerrar O2, y una segunda que abre el lado caliente— y se pregunta si con ese par el ciclo converge y es KALINA. Si la respuesta es sí, interesa además cuánto hay que mover cada una.
## 2. Qué se hizo
- **Las dos rutas.** Ruta A (solo diseño): `eps_hrvg` ∈ {{0.75, 0.78, 0.81}}, con toda la fuente y el sitio del profesor (T_fuente = 623.15 K). Ruta B (sitio + diseño): `T_fuente` ∈ {{380, 390, 403, 420, 434, 466, 497, 529, 560}} K, con todo lo demás del profesor (eps_hrvg = 0.85). En ambas rutas las otras nueve variables quedan exactamente como él las dio.
- **La malla.** Para cada valor de la variable 1, `P_baja` recorre `numpy.linspace(400, 2000, 12)`: (3 + 9) × 12 = 144 corridas con 6 procesos.
- **La bisección.** Entre cada par de vecinos de la malla donde cambia ser KALINA, o donde cambia `m_O2 >= 0` (solo cuando ambos vecinos son genuinos), se parte el intervalo por la mitad hasta acotar la frontera a 10 kPa o agotar 8 iteraciones, ronda a ronda en paralelo.
- **Punto genuino.** Solo cuentan como converge los puntos `KALINA`, `CORREGIBLE` e `INVIABLE`; una fila que el solver cerró pero que el clasificador marca `NO_CONVERGIO` es un punto fijo espurio (N2) y se trata como NO convergido en conteos, fronteras y conclusiones.
- **Escala de `d`.** El índice de cercanía usa los rangos del nivel 1: eps_hrvg [0.75, 0.85], T_fuente [340, 623.15] y P_baja [150, 1500] kPa, **aunque la malla de este nivel llegue a 2000 kPa**: un KALINA por encima de 1500 kPa queda con d > 1.
## 3. Tabla por ruta (una fila por valor de la variable 1)

{s3}
## 4. KALINA de menor d y de mayor η, por ruta

{_tabla_kalina(kal)}
## 5. Tiempos
{s5}
## 6. Conclusión
{s6}
## 7. Lo que no se sabe
{chr(10).join(s7)}
## 8. Qué sigue
El siguiente paso lo decide el director a partir de las tablas de §3 y §4: aquí no se proponen valores concretos, solo los dos extremos medidos de cada frontera.
"""
    (n2.OUT / "REPORTE_M2_N2.md").write_text(doc, encoding="utf-8")
    print("REPORTE_M2_N2.md escrito", flush=True)


def generar(malla, bise, fr, t_malla, t_bise) -> None:
    """CSVs de resumen y reporte, a partir de las filas de las dos fases."""
    todo = malla + bise
    fron = filas_fronteras(fr)
    escribir("m2n2_fronteras.csv", CFRON, fron)
    kal = filas_kalina(todo)
    escribir("m2n2_kalina.csv", CKAL, kal)
    res = filas_resumen(todo)
    escribir("m2n2_resumen.csv", CREST, res)
    reporte(kal, res, fron, todo, t_malla, t_bise)


if __name__ == "__main__":
    raise SystemExit("Importar y llamar generar(); la corrida es m2_nivel2.py")
