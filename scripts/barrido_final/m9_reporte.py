"""M9 — paso 4: `REPORTE_M9.md` en lenguaje llano.

Escribe la pregunta, qué se hizo, la tabla de la escalera, el conjunto máximo de
datos del profesor compatible con KALINA con los rangos de lo que queda libre, el
grupo que bloquea, Húsavík y los 3 puntos del motor real. Todas las cifras se
leen de los CSV; no se inventa nada.
"""
from __future__ import annotations

import sys  # noqa: E402
from pathlib import Path

_DIR = Path(__file__).resolve().parent
_RAIZ = _DIR.parents[1]
sys.path[:0] = [str(_RAIZ), str(_DIR)]

import m9_datos as m9  # noqa: E402


def _fmt(x, d=3):
    """Número con `d` cifras significativas, o cadena vacía si es `None`."""
    return "" if x is None else f"{x:.{d}g}"


def maximo(esc_rows: list):
    """`(mejor conjunto con KALINA, conjuntos rescatados)` de la escalera."""
    eleg = [e for e in esc_rows if e["elegido"]]
    con_k = [e for e in eleg if (e["n_kalina"] or 0) > 0]
    return (con_k[-1] if con_k else None,
            [e for e in esc_rows if e["kalina_por_busqueda"]])


def husavik_parrafo() -> str:
    """Frase con la P_baja mínima KALINA por piso y la η a 690 kPa."""
    hus = m9.leer(m9.OUT / "m9_husavik.csv")
    if not hus:
        return "No se corrió el paso 0."
    partes = []
    for piso in sorted({f["piso_tamb"] for f in hus}):
        k = [f for f in hus if f["piso_tamb"] == piso and m9.es_kalina(f)]
        if k:
            partes.append(f"con el piso {piso:g} K hay KALINA desde "
                          f"P_baja = {min(f['P_baja_test'] for f in k):g} kPa")
        else:
            partes.append(f"con el piso {piso:g} K no hubo KALINA en la malla")
    eta = [f for f in hus if f["P_baja_test"] == 690.0 and m9.es_kalina(f)]
    t = (f" η a 690 kPa: {_fmt(eta[0]['eta'])}." if eta else
         " A 690 kPa no hubo KALINA en la malla.")
    return "En la malla de P_baja 500–1000 kPa: " + "; ".join(partes) + "." + t


def motor_parrafo() -> str:
    """Tabla de los 3 puntos del motor real frente a teqp."""
    mr = m9.leer(m9.OUT / "m9_motor_real.csv")
    if not mr:
        return "No se corrió el paso 3."
    L = ["| punto | clase teqp | clase real | η teqp | η real | d_eta_pp (pp) |",
         "|---|---|---|---|---|---|"]
    for f in mr:
        L.append(f'| {f["id"]} | {f["clase_teqp"]} | {f["clase_real"]} | '
                 f'{_fmt(f["eta_teqp"])} | {_fmt(f["eta_real"])} | '
                 f'{_fmt(f["d_eta_pp"])} |')
    return "\n".join(L)


def _bloqueo(esc_rows: list, rescate: list) -> list:
    """Frases sobre el grupo que bloquea y los conjuntos rescatados."""
    L = []
    p = m9.OUT / "m9_paso2_corte.txt"
    motivo = p.read_text(encoding="utf-8").strip() if p.exists() else ""
    rmax = 2 if m9.HUMO else 3
    if esc_rows:
        ult = max(e["ronda"] for e in esc_rows)
        for e in [e for e in esc_rows if e["ronda"] == ult and e["elegido"]]:
            if (e["n_kalina"] or 0) == 0:
                L.append(f"El grupo que rompe el ciclo es el último sumado para "
                         f"llegar a `{e['conservados']}`: ese conjunto dio 0 "
                         f"KALINA (criterio más frecuente: "
                         f"{e['criterio_mas_roto'] or '—'}).")
            else:
                L.append(f"El conjunto `{e['conservados']}` todavía da KALINA.")
        if "3 h 15" in motivo and ult < rmax:
            L.append(f"El paso 2 se detuvo tras la ronda {ult} — {motivo}. Las "
                     f"rondas siguientes (hasta conservar 4 grupos) quedaron "
                     f"**no exploradas**; eso no significa 'sin KALINA'.")
    for e in rescate:
        L.append(f"- La búsqueda dirigida sobre `{e['conservados']}` "
                 f"{'sí' if e['kalina_por_busqueda'] else 'no'} encontró KALINA "
                 f"(el LHS original no la vio).")
    return L


def _rango_libre(m: dict, ran: list, esc: dict) -> list:
    """Bullets con los rangos KALINA de cada variable libre del conjunto máximo."""
    L = []
    for key, (codes, _rows) in esc.items():
        if key != m["conservados"]:
            continue
        for v in m9.libres(codes) + ["dP", "rP"]:
            s = next((r for r in ran if r["conjunto"] == key
                      and r["ambito"] == "todos los KALINA"
                      and r["variable"] == v), None)
            if s:
                L.append(f"- `{v}`: KALINA en {_fmt(s['min'])} – {_fmt(s['max'])} "
                         f"(mediana {_fmt(s['mediana'])}, n={s['n']}).")
    return L


def escribir(ran: list, esc_rows: list, esc: dict) -> int:
    """Escribe `REPORTE_M9.md` y devuelve su número de líneas."""
    m, rescate = maximo(esc_rows)
    L = ["# REPORTE M9 — escalera de conservación de los datos del profesor", "",
         "## La pregunta",
         "¿Qué datos del profesor se pueden conservar tal cual y aun así obtener "
         "un ciclo KALINA? ¿Cuál es el conjunto máximo de sus datos compatible "
         "con KALINA? Para cada conjunto, ¿en qué rangos quedan las demás "
         "variables, sobre todo P_alta, P_baja, dP = P_alta − P_baja y "
         "rP = P_alta/P_baja? La eficiencia es secundaria.",
         "", "## Qué se hizo",
         "Se evaluó el ciclo con `comun.evaluar_punto` (motor teqp) sobre un "
         "barrido LHS. Paso 1: conservar un grupo del profesor. Paso 2: sumar "
         "grupos de a uno (selección hacia adelante) hasta que el conjunto "
         "máximo deje de dar KALINA. Paso 3: 3 puntos de control con el motor "
         "real. Todo con `ProcessPoolExecutor(max_workers=7)`.",
         "", "## La escalera", "",
         "| ronda | conservados | n.º de datos | n corridas | genuinos | "
         "KALINA | KALINA confiables | D mín | criterio más roto | elegido |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for e in sorted(esc_rows, key=lambda r: (r["ronda"], r["conservados"])):
        L.append(f'| {e["ronda"]} | {e["conservados"]} | {e["n_conservadas"]} | '
                 f'{e["n_eval"]} | {e["n_genuinos"]} | {e["n_kalina"]} | '
                 f'{e["n_kalina_confiable"]} | {_fmt(e["D_min"])} | '
                 f'{e["criterio_mas_roto"] or "—"} | '
                 f'{"sí" if e["elegido"] else "no"} |')
    L += ["", "## El conjunto máximo de datos del profesor compatible con KALINA"]
    if m is None:
        L.append("Ningún conjunto conservado dio KALINA. El conjunto máximo es "
                 "el vacío: bastan los datos del profesor para bloquear el "
                 "ciclo en toda la caja explorada.")
    else:
        L.append(f"Se conservan **{m['n_conservadas']} datos del profesor** "
                 f"(grupos `{m['conservados']}`) y aun así hay KALINA: "
                 f"{m['n_kalina']} KALINA ({m['n_kalina_confiable']} "
                 f"confiables) en {m['n_eval']} corridas.")
        L += _rango_libre(m, ran, esc)
    L += ["", "## Qué bloquea"] + _bloqueo(esc_rows, rescate)
    L += ["", "## Húsavík", husavik_parrafo(),
          "", "## Los 3 puntos del motor real", motor_parrafo(),
          "", "## Lo que no se sabe",
          "- El barrido es por muestreo (LHS + búsqueda por patrones): un "
          "conjunto que dio 0 KALINA en la muestra puede tener franjas angostas "
          "no vistas (la búsqueda dirigida lo mitiga para la última ronda).",
          "- Las corridas usan presupuestos de tiempo fijos (teqp 300 s, motor "
          "real 1500 s); un punto en el borde del presupuesto puede no converger.",
          "- El reporte de rangos vale para la caja explorada, no fuera de ella.",
          ""]
    txt = "\n".join(L)
    (m9.OUT / "REPORTE_M9.md").write_text(txt, encoding="utf-8")
    return len(txt.splitlines())
