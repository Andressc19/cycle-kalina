"""M5 — `REPORTE_M5.md` en lenguaje llano (TASK_CONTEXT final_M5 §Reporte).

Lo llama `m5_analisis.main()` con las filas de `m5_resumen.csv`,
`m5_rangos.csv` y `m5_cercano_profesor.csv` ya calculadas. TODAS las cifras
del documento salen de esos tres objetos (y los tiempos de `stdout.txt`, con
el mismo `_tiempo` que usó M4b, importado sin modificarlo), para que
`m5_verificar.py` pueda reconstruir el texto entero desde los CSV y exigir
que sea idéntico.
"""
from __future__ import annotations
import sys
from pathlib import Path
_DIR = Path(__file__).resolve().parent
_RAIZ = _DIR.parents[1]
sys.path[:0] = [str(_RAIZ), str(_DIR)]
from comun import PROFESOR
from m4_tablas import gf, nf
from m4b_reporte import _tiempo
from m5_corrida import FIJOS, LIBRES, OUT
# Nombre de cada escenario, tal como lo nombra el TASK_CONTEXT §Escenarios.
NOMBRES = {1: "sus temperaturas", 2: "sus presiones",
           3: "sus presiones y su clima", 4: "su P_alta y sus temperaturas",
           5: "su fuente y su composición"}
# Rangos clave que van en la tabla principal (p5–p95 dentro de KALINA).
CLAVES = {1: ("P_alta", "P_baja", "dP", "rP", "x_b"),
          2: ("T_fuente", "T_sumidero", "x_b"), 3: ("T_fuente", "x_b"),
          4: ("P_baja", "dP", "rP", "x_b"),
          5: ("P_alta", "P_baja", "dP", "rP", "T_sumidero")}
UNID = {"P_alta": " kPa", "P_baja": " kPa", "dP": " kPa",
        "T_fuente": " K", "T_sumidero": " K"}
CAB3 = ("| escenario | qué se conserva | ¿hay KALINA? | cuántos | rangos clave "
        "de lo que se mueve (p5–p95 en KALINA) | KALINA más parecido (id, d) | "
        "η de ese punto |")


def _fijo(k: int) -> str:
    """`T_fuente = 623.15, T_sumidero = 300.032917` (valores exactos)."""
    return ", ".join(f"{v} = {PROFESOR[v]}" for v in FIJOS[k])


def _cer(cer: list, k: int, tipo: str):
    return next((c for c in cer if c["escenario"] == k and c["tipo"] == tipo), None)


def _rango_clave(k: int, rang: list) -> str:
    """`P_alta 2155.69–4841.78 kPa; …` (p5–p95 de las claves, en KALINA)."""
    out = []
    for v in CLAVES[k]:
        r = next((x for x in rang if x["escenario"] == k
                  and x["variable"] == v and x["grupo"] == "KALINA"
                  and x["n"]), None)
        if r:
            out.append(f"{v} {gf(r['p05'])}–{gf(r['p95'])}{UNID.get(v, '')}")
    return "; ".join(out) or "—"


def _tabla3(res: list, rang: list, cer: list) -> str:
    """§3: la tabla principal, una fila por escenario."""
    lin = [CAB3, "|---|---|---|---|---|---|---|"]
    for r in res:
        k, c, sim = r["escenario"], _cer(cer, r["escenario"], "cercano"), \
            "sí" if r["factible"] else "NO"
        cer_t = "—" if c is None else f'id {c["id"]}, d = {gf(c["d"])}'
        eta_t = "—" if c is None else nf(c["eta"], 4)
        lin.append(f'| S{k} ({NOMBRES[k]}) | {_fijo(k)} | {sim} | '
                   f'{r["KALINA"]} KALINA / {r["evaluados"]} evaluados | '
                   f'{_rango_clave(k, rang) if r["factible"] else "—"} | '
                   f'{cer_t} | {eta_t} |')
    return "\n".join(lin)


def _tabla4(k: int, rang: list) -> str:
    """§4: rangos de las variables libres (más dP y rP) DENTRO de KALINA."""
    vs = list(LIBRES[k])
    vs += ["dP", "rP"] if ("P_alta" in LIBRES[k] or "P_baja" in LIBRES[k]) else []
    lin = ["| variable | n | mín | p5 | mediana | p95 | máx | KS | valor p |",
           "|---|---|---|---|---|---|---|---|---|"]
    for v in vs:
        r = next(x for x in rang if x["escenario"] == k
                 and x["variable"] == v and x["grupo"] == "KALINA")
        lin.append(f'| {v} | {r["n"]} | {gf(r["min"])} | {gf(r["p05"])} | '
                   f'{gf(r["mediana"])} | {gf(r["p95"])} | {gf(r["max"])} | '
                   f'{nf(r["KS"], 3)} | {nf(r["p_valor"], 4)} |')
    return "\n".join(lin)


def _punto(c: dict) -> str:
    """El punto de `m5_cercano_profesor.csv` con todos sus valores."""
    vals = ", ".join(f"{v} = {gf(c[v])}" for v in LIBRES[c["escenario"]])
    return (f'id {c["id"]}, d = {gf(c["d"])}, η = {nf(c["eta"], 4)}, D = '
            f'{gf(c["D"])}, fuera de rango = {"sí" if c["fuera_rango"] else "no"}, '
            f'B_verificado = {c["B_verificado"] or "sin error"}. '
            f'Sus valores: {vals}')


def _bloqueo(r: dict) -> str:
    if not r["bloqueante"]:
        return "No hay genuinos sin KALINA: ningún criterio se rompe."
    return (f'El criterio que bloquea al resto es `{r["bloqueante"]}`: '
            f'{r["bloqueante_n"]} de los {r["genuinos"] - r["KALINA"]} '
            f'genuinos no KALINA.')


def _seccion(r: dict, rang: list, cer: list) -> str:
    """§4: una sección por escenario, con rangos, figura y criterio bloqueante."""
    k = r["escenario"]
    txt = [f'### 4.{k} — S{k}: {NOMBRES[k]} (conserva {_fijo(k)})\n',
           f'Puntos: {r["n"]} por escenario; omitidos por la restricción '
           f'`P_baja ≥ P_alta − 300`: {r["omitidos"]}; evaluados: '
           f'{r["evaluados"]}. KALINA = {r["KALINA"]}, genuinos = '
           f'{r["genuinos"]}, espurios N2 = {r["N2"]}, fuera de rango = '
           f'{r["fuera_rango"]}.\n\n']
    if r["factible"]:
        c, b = _cer(cer, k, "cercano"), _cer(cer, k, "mejor_eta")
        txt.append(f'Rangos de las variables libres **dentro de los '
                   f'{r["KALINA"]} KALINA** (el KS es KALINA contra no KALINA, '
                   f'solo con ≥ 10 KALINA):\n\n{_tabla4(k, rang)}\n\n')
        txt.append(f'La figura, solo con los {r["evaluados"]} puntos evaluados '
                   f'y coloreada por clase:\n\n![Ventana S{k}](m5_S{k}.png)\n\n')
        txt.append(f'El KALINA más parecido al profesor (menor '
                   f'd = Σ|v − v_prof|/(b − a) sobre las libres): '
                   f'{_punto(c)}\n\n' if c else '')
        txt.append(f'Secundario, el KALINA de mayor η: {_punto(b)}\n\n' if b else '')
        txt.append(_bloqueo(r) + "\n")
    else:
        md = _cer(cer, k, "genuino_mD")
        txt.append(f'**No factible en esta caja:** de los {r["evaluados"]} '
                   f'puntos evaluados, ninguno quedó KALINA.\n\n')
        txt.append(_bloqueo(r) + "\n\n")
        txt.append(f'El punto genuino de menor D (D = Σviolaciones/τ, cuanto '
                   f'más cerca de factible) es: {_punto(md)}\n' if md else "")
    return "".join(txt)


def _conclusion(r: dict, rang: list, cer: list) -> str:
    """§6: la forma obligatoria "De los datos del profesor se pueden conservar…"."""
    k = r["escenario"]
    if r["factible"]:
        c = _cer(cer, k, "cercano")
        return (f'- **S{k} — {NOMBRES[k]}:** de los datos del profesor se pueden '
                f'conservar **{_fijo(k)}** siempre que las variables libres '
                f'queden en {_rango_clave(k, rang)} (p5–p95 de los '
                f'{r["KALINA"]} KALINA; el más parecido al profesor es el id '
                f'{c["id"]}, con η = {nf(c["eta"], 4)}).')
    return (f'- **S{k} — {NOMBRES[k]}:** con **{_fijo(k)}** fijos no se pudo: '
            f'de {r["evaluados"]} puntos evaluados, 0 KALINA. El criterio que '
            f'más se rompe es `{r["bloqueante"] or "ninguno"}` '
            f'({r["bloqueante_n"]} puntos) y el genuino de menor D '
            f'(D = {gf(r["mejor_D"])}) es el id {r["mejor_D_id"]}.')


def _doc(res: list, cer: list, rang: list) -> str:
    """El `REPORTE_M5.md` entero, solo con los tres CSV y `stdout.txt`."""
    n0, tot = res[0]["n"], sum(r["n"] for r in res)
    om, ev = sum(r["omitidos"] for r in res), sum(r["evaluados"] for r in res)
    nk, fr = sum(r["KALINA"] for r in res), sum(r["fuera_rango"] for r in res)
    tempos = ", ".join(f'S{r["escenario"]} = {nf(r["suma_t_s"], 1)} s' for r in res)
    p1 = (f"# REPORTE M5 — regiones KALINA conservando datos del profesor\n"
          f"## 1. La pregunta\n"
          f"**¿Qué datos del profesor se pueden conservar tal cual y aun así obtener un ciclo KALINA?** Para cada conjunto conservado, ¿en qué rangos tienen que estar las demás variables, en especial las presiones y sus diferencias? La eficiencia es secundaria: se reporta, pero no se optimiza.\n"
          f"## 2. Qué se hizo\n"
          f"- **Cinco escenarios.** En cada uno se fija un subconjunto de los datos del profesor (`comun.PROFESOR`) y el resto queda libre dentro de la caja de M5 (P_alta 2000–5000 kPa, P_baja 200–2000 kPa, T_fuente 380–623.15 K, T_sumidero 278.15–303.55 K, x_b 0.50–0.85 y las efectividades 0.40–0.95). Por escenario, un LHS de {n0} puntos sobre sus variables libres con `scipy.stats.qmc.LatinHypercube(d=n_libres, seed=20261007 + k)` (k = 1…5). La muestra quedó en `m5_muestra.csv` ANTES de correr.\n"
          f"- **Corrida.** {tot} corridas en un solo `ProcessPoolExecutor(max_workers=7)`, motor `teqp`, piso de O2 de cada punto igual a su propia `T_sumidero`. Todo quedó en `m5_lhs.csv` con las columnas `escenario, id, omitido` más las de `COLS`.\n"
          f"- **Restricción física.** Si `P_baja ≥ P_alta − 300` el punto no se evalúa: `omitido=True` con el motivo en `mensaje` ({om} de {tot} puntos).\n"
          f"- **Punto genuino (igual que M4).** Solo cuentan KALINA, CORREGIBLE e INVIABLE; una fila con `convergio=True` y NO_CONVERGIO es espuria (N2) y es NO genuina en todo.\n"
          f"- **Análisis.** Por escenario: conteos, ¿es posible?, rangos (mín, p5, mediana, p95, máx) de cada variable libre dentro de KALINA con el KS (RSA) cuando hay ≥ 10 KALINA, la figura de la ventana, el KALINA más parecido al profesor y, secundario, el de mayor η. De {ev} evaluados salieron **{nk} KALINA**.\n"
          f"## 3. Tabla principal\n")
    p2 = ["\n## 4. Un escenario por escenario\n"]
    for r in res:
        p2.append(_seccion(r, rang, cer) + "\n\n")
    p3 = (f"## 5. Los tiempos\nLa corrida: {_tiempo(OUT)}. Suma de los "
          f"tiempos de cómputo de los {ev} puntos evaluados por escenario: "
          f"{tempos}.\n"
          f"## 6. La conclusión\n"
          + "\n".join(_conclusion(r, rang, cer) for r in res) + "\n"
          f"## 7. Lo que no se sabe\n"
          f"- {n0} puntos por escenario es una **exploración**, no un mapa fino: sirve para decir qué escenario es factible y qué criterio bloquea, no para cerrar rangos.\n"
          f"- Los puntos **fuera de rango** (motor de propiedades sin respaldo experimental): {fr} de {ev} evaluados. Sus η hay que tomarlas con pinzas.\n"
          f"- Los {om} puntos omitidos no se evaluaron: no dicen nada sobre el ciclo, solo que sus presiones estaban demasiado pegadas.\n"
          f"- La caja de las variables libres la fijó el director; fuera de ella no se dijo nada.\n"
          f"## 8. Qué sigue\n"
          f"Que el director elija qué escenario llevar a un mapa fino (más puntos por escenario) y si conviene aflojar o no la restricción `P_baja ≥ P_alta − 300`, que es la que descarta los {om} puntos omitidos.\n")
    return p1 + _tabla3(res, rang, cer) + "\n" + "".join(p2) + p3


def generar(res: list, cer: list, rang: list) -> None:
    (OUT / "REPORTE_M5.md").write_text(_doc(res, cer, rang), encoding="utf-8")
    print("REPORTE_M5.md escrito", flush=True)
