"""M4b — `REPORTE_M4b.md` en lenguaje llano (TASK_CONTEXT final_M4b §Reporte).

Lo llama `m4b_analisis.main()` con las filas de los 500 puntos y los resultados
ya calculados. Las tablas de presiones las arma `m4b_tablas.py`, las del resto
`m4_tablas.py`, y las cifras salen de los mismos objetos que se escriben a los
CSV, para que la verificación pueda contrastarlas. La prioridad va primero: la
ventana de presiones de KALINA (§4–§6) antes que η y el resto.
"""
from __future__ import annotations

import re, sys  # noqa: E401,E402
from pathlib import Path

_DIR = Path(__file__).resolve().parent
_RAIZ = _DIR.parents[1]
sys.path[:0] = [str(_RAIZ), str(_DIR)]

from m4_analisis import N_MINIMO, resumen  # noqa: E402
from m4_tablas import gf, nf  # noqa: E402
from m4_tablas import tabla_pawn, tabla_prcc, tabla_rsa, tabla_top  # noqa: E402
from m4b_datos import OUT, OUT4, leer_plano  # noqa: E402
from m4b_tablas import prosa_franjas, suma_zonas  # noqa: E402
from m4b_tablas import tabla_b, tabla_cmp, tabla_fr, tabla_g  # noqa: E402

RUTAS = (("P_alta", "P_alta"), ("T_fuente", "T_fuente"),
         ("T_sumidero", "T_sumidero"))
CUMPLE = ("cumple el criterio ρ ≥ 0.9", "NO cumple el criterio ρ ≥ 0.9")


def _rsa300() -> dict:
    """El RSA separación KALINA de los 300 de M4, leído de su `m4_rsa.csv`."""
    def num(c):
        return None if c in (None, "") else float(c)
    return {r["variable"]: dict(KS=num(r["KS"]), fav_p05=num(r["fav_p05"]),
                                fav_p95=num(r["fav_p95"]))
            for r in leer_plano(OUT4, "m4_rsa.csv")
            if r["separacion"] == "KALINA"}


def _tiempo(d) -> str:
    """`(txt)` con las corridas de `d/stdout.txt`; sin archivo, se dice."""
    p = Path(d) / "stdout.txt"
    if not p.exists():
        return "no hay `stdout.txt` con el tiempo total"
    for enc in ("utf-8", "utf-16", "cp1252", "latin-1"):
        try:
            m = re.search(r"fin: (\d+) corridas en (\d+) s",
                          p.read_bytes().decode(enc))
        except (UnicodeDecodeError, ValueError):
            continue
        if m:
            return (f"tardaron {m.group(2)} s ({int(m.group(2)) // 60} min) "
                    f"en {m.group(1)} corridas")
    return "no se encontró la línea `fin:` en `stdout.txt`"


def _reglas(cart) -> list:
    """Las hojas del árbol, tal como quedaron escritas en `m4b_cart.txt`."""
    trozo = (cart.get("texto") or "").split("reglas en palabras:")[-1]
    lin = [l for l in trozo.splitlines() if l.startswith("- si ")]
    return lin or ["- (no hay árbol: faltan las dos clases)"]


def _rho_cum(conv) -> dict:
    """`(métrica → (ρ, cumple))` de `m4b_convergencia.csv`."""
    return {r["metrica"]: (r["rho_spearman"], r["cumple_09"]) for r in conv
            if r["rho_spearman"] is not None}


def _tupla(rangos, v):
    """`(p5, p95)` de la variable `v` dentro de KALINA, desde la tabla (b)."""
    r = next(x for x in rangos if x["variable"] == v and x["grupo"] == "KALINA")
    return r["p05"], r["p95"]


def _cabecera(res, clases, nk) -> str:
    return f"""# REPORTE M4b — 500 puntos, foco en las presiones de KALINA
## 1. La pregunta
Lo primero ahora son **los rangos donde hay KALINA**, en particular **las presiones alta y baja y sus diferencias**: dP = P_alta − P_baja y rP = P_alta/P_baja. La pregunta es: **¿en qué ventana de P_alta, P_baja, dP y rP vive KALINA?, ¿cómo cambia esa ventana según la temperatura de la fuente y la del sumidero? y ¿qué criterio se rompe fuera de ella?** La eficiencia η es secundaria.
## 2. Qué se hizo
- **Muestreo nuevo.** 200 puntos con muestreo latino hipercubo (LHS, semilla 20261007) sobre la **misma caja de 10 variables** de M4, con `id_muestra` de 300 a 499. La muestra quedó en `m4b_muestra.csv` ANTES de correr.
- **Corrida.** Los 200 puntos se resolvieron con el motor `teqp` y 7 procesos, con el piso de O2 de cada punto igual a su propia `T_sumidero` (igual que M4). Todo quedó en `m4b_lhs.csv`.
- **Unión.** 300 (M4, semilla 20261006) + 200 (M4b, semilla 20261007) = **500 puntos**. **La unión de dos LHS no es un LHS estricto de 500**: los cortes de una muestra no caen necesariamente en el centro de las franjas de la otra. **Pero cada mitad sí lo es** —los 300 tienen la propiedad LHS con sus 300 franjas y los 200 con sus 200—.
- **Punto genuino (igual que M4).** Solo cuentan KALINA, CORREGIBLE e INVIABLE. Una fila que el solver cerró pero que el clasificador marca NO_CONVERGIO es un punto fijo espurio (N2) y es NO genuina en todo.
- **Análisis.** Se repitió el análisis de M4 sobre los 500 con las mismas fórmulas y parámetros: RSA con sus 4 separaciones (13 variables), PAWN, PRCC, CART, convergencia (aquí 300 vs 500) y top-10.
- **Presiones (lo nuevo).** Plano de P_baja contra P_alta, rangos de P_alta/P_baja/dP/rP dentro y fuera de KALINA, ventanas por P_alta, T_fuente y T_sumidero, histogramas y bloqueo por rP.
## 3. Conteos
De **{res['n']}** puntos: **{nk} KALINA**. Conteos por clase: {clases}.
Los primeros 300 son de M4 y los 200 nuevos de M4b. Puntos genuinos: {res['n_genuinos']}. Espurios N2 (`convergio=True` y NO_CONVERGIO): {res['n_N2']}. Fuera del rango confiable del motor de propiedades: {res['n_fuera']}.
"""


def _sec_presiones(rangos, fr) -> str:
    """§4 (tabla b + figura a) y §5 (prosa y tabla por cada variable)."""
    txt = ["""## 4. La ventana de presiones de KALINA
La tabla (b) da, para P_alta, P_baja, dP y rP, el mínimo, el p5, la mediana, el p95 y el máximo **dentro de KALINA**, los mismos estadísticos de los genuinos que NO son KALINA, y el KS con su valor p que separa a los dos grupos. Cuanto más alto el KS, más distintas son las dos distribuciones.

""", tabla_b(rangos), """

La figura (a) muestra los 500 puntos en el plano P_baja (x) contra P_alta (y), con el color de su clase y las líneas de rP constante en 2, 3, 4 y 5:

![Plano de presiones](m4b_plano_presiones.png)
## 5. Cómo cambia la ventana de P_baja, dP y rP según P_alta, T_fuente y T_sumidero
Cada variable se corta en franjas iguales; dentro de cada una se cuentan los puntos y los KALINA, y se dan los rangos (mín–máx) de P_baja, dP y rP **solo de los KALINA**.
"""]
    for i, (v, nom) in enumerate(RUTAS, 1):
        a, b = fr[v][0]["lo"], fr[v][-1]["hi"]
        txt.append(f"\n### 5.{i} Según {nom}: {len(fr[v])} franjas de "
                   f"{gf(a)} a {gf(b)}\n\n")
        txt.append(". ".join(p for p in prosa_franjas(fr[v], v)) + ".\n\n")
        txt.append(tabla_fr(fr[v]) + "\n")
    return "".join(txt)


def _doc(filas, rsa, pawn, prcc, cart, conv, top, pdat, chicos) -> str:
    res = resumen(filas)
    nk = res["conteos"].get("KALINA", 0)
    clases = ", ".join(f"{k} = {v}" for k, v in res["conteos"].most_common())
    rangos, fr, blk = pdat["rangos"], pdat["franjas"], pdat["bloqueo"]
    rp05, rp95 = pdat["rp_kalina"]
    k500 = [r for r in rsa if r["separacion"] == "KALINA"]
    rho = _rho_cum(conv)
    rks, cks = rho.get("KS_KALINA", (None, False))
    rpr, cpr = rho.get("PRCC_eta", (None, False))
    aviso = (f"Ningún grupo quedó por debajo de {N_MINIMO} puntos."
             if not chicos else
             f"**Aviso:** estos grupos quedaron con menos de {N_MINIMO} "
             "puntos y NO se amplió el muestreo por cuenta propia (el "
             "director decide):\n" + "\n".join(f"- `{c}`" for c in chicos))
    bloq_tot = ", ".join(f"{z} = {n}" for z, n in suma_zonas(blk).items())
    rangos_rec = "\n".join(
        f"- **{v}:** [{gf(a)}, {gf(b)}]" + (" kPa" if v != "rP" else "")
        for v in ("P_alta", "P_baja", "dP", "rP")
        for a, b in [_tupla(rangos, v)])
    doc = [_cabecera(res, clases, nk), _sec_presiones(rangos, fr)]
    doc.append(f"""
## 6. Qué criterio se rompe fuera de la ventana
Entre los genuinos NO KALINA se cuenta `codigos_falla` según el rP caiga por debajo del p5 de KALINA ({gf(rp05)}), por encima del p95 ({gf(rp95)}) o dentro del intervalo. Totales por zona: {bloq_tot}.

{tabla_g(blk)}

Los histogramas de dP y de rP, KALINA contra no KALINA:

![Histogramas dP y rP](m4b_hist_dP_rP.png)
## 7. El RSA con 500 puntos, comparado con los 300
Rangos favorables (p5–p95 dentro de KALINA) y KS con los 500, junto a los mismos números de los 300 de M4:

{tabla_cmp(k500, _rsa300())}

La tabla completa con 500 (IC95 % por bootstrap, valor p y tamaños de grupo):

{tabla_rsa(k500)}

{aviso}
## 8. La convergencia
ρ de Spearman entre el ranking con los 300 puntos y el de los 500, con el criterio **ρ ≥ 0.9**: **KS (KALINA) = {nf(rks, 4)}** ({CUMPLE[0 if cks else 1]}) y **PRCC(η) = {nf(rpr, 4)}** ({CUMPLE[0 if cpr else 1]}).
## 9. PRCC y PAWN sobre η (secundario)
**PAWN** (10 franjas; cuanto más alto el índice, más cambia la distribución al fijar la variable):

{tabla_pawn(pawn)}

**PRCC** (negativo = subir la variable baja η; el IC95 % que no cruza al cero indica que el efecto se distingue del ruido):

{tabla_prcc(prcc)}
## 10. Las reglas de CART
Clasificador CART (`max_depth=4`, `min_samples_leaf=5`, `random_state=0`) sobre las 10 variables, KALINA vs no KALINA. {cart['acc']}.
{chr(10).join(_reglas(cart))}
## 11. El top-10 KALINA (secundario)
Los {len(top)} KALINA de mayor η de los 500:

{tabla_top(top)}
## 12. Los tiempos
M4b (los 200 nuevos): {_tiempo(OUT)}. M4 (los 300 anteriores): {_tiempo(OUT4)}.
## 13. La conclusión: los rangos recomendados de P_alta, P_baja, dP y rP para KALINA
Los percentiles 5–95 de cada presión **dentro de los {nk} KALINA** (misma definición de rango favorable que el RSA):

{rangos_rec}

Estos son los rangos donde vive KALINA en esta caja de 500 puntos; la ventana de rP ({gf(rp05)}–{gf(rp95)}) es la que separa a los KALINA del resto en §6. No se propuso ningún valor nuevo: las tablas son insumos para que el director decida.
## 14. Lo que no se sabe
- La unión de dos LHS **no es un LHS estricto de 500**; solo cada mitad lo es (§2).
- Las diferencias de η menores que 0.4–0.7 pp no son concluyentes: es la banda de incertidumbre del modelo de propiedades (G4-01).
- Hay puntos fuera de rango (motor de propiedades sin respaldo experimental): {res['n_fuera']} de {res['n']}. Sus η hay que tomarlas con pinzas.
- Es una **caja favorable**, no todo el espacio: fuera de los rangos de `TASK_CONTEXT final_M4` no se dijo nada.
- Las franjas con pocos KALINA (§5) dan rangos poco confiables.
## 15. Qué sigue
M5 (búsqueda dirigida hacia KALINA dentro de la ventana de presiones de §13). El orden concreto lo decide el director.
""")
    return "".join(doc)


def generar(filas, rsa, pawn, prcc, cart, conv, top, pdat, chicos) -> None:
    (OUT / "REPORTE_M4b.md").write_text(
        _doc(filas, rsa, pawn, prcc, cart, conv, top, pdat, chicos),
        encoding="utf-8")
    print("REPORTE_M4b.md escrito", flush=True)
