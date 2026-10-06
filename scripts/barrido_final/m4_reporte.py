"""M4 — `REPORTE_M4.md` en lenguaje llano (TASK_CONTEXT final_M4 §Reporte).

Lo llama `m4_analisis.main()` con las filas de `m4_lhs.csv` y los resultados ya
calculados; las tablas las arma `m4_tablas.py` y las cifras salen de los CSV,
para que la verificación pueda contrastarlas.
"""
from __future__ import annotations

import re, sys  # noqa: E401,E402
from pathlib import Path

_DIR = Path(__file__).resolve().parent
_RAIZ = _DIR.parents[1]
sys.path[:0] = [str(_RAIZ), str(_DIR)]

from m4_analisis import N_MINIMO, resumen  # noqa: E402
from m4_datos import DERIV, OUT, VARS10  # noqa: E402
from m4_tablas import gf, icf, nf, pf  # noqa: E402
from m4_tablas import tabla_pawn, tabla_prcc, tabla_rsa, tabla_top  # noqa: E402


def _tiempos(filas):
    """`(txt)` con el total de stdout.txt y las estadísticas de `t_s`."""
    ts = sorted(f["t_s"] for f in filas if f["t_s"] is not None)
    txt = "El tiempo total de la corrida no está en stdout.txt."
    p = OUT / "stdout.txt"
    if p.exists():
        for enc in ("utf-8", "utf-16", "cp1252", "latin-1"):
            try:
                m = re.search(r"fin: (\d+) corridas en (\d+) s",
                              p.read_bytes().decode(enc))
            except (UnicodeDecodeError, ValueError):
                continue
            if m:
                txt = (f'La corrida completa ({m.group(1)} corridas) tardó '
                       f'{m.group(2)} s ({int(m.group(2)) // 60} min).')
                break
    if ts:
        txt += (f" Por punto (`t_s`): mínimo {nf(ts[0], 1)} s, mediana "
                f"{nf(ts[len(ts) // 2], 1)} s, máximo {nf(ts[-1], 1)} s, "
                f"media {nf(sum(ts) / len(ts), 1)} s ({len(ts)} puntos).")
    return txt


def _rho(conv):
    """`(métrica → ρ de Spearman)` de `m4_convergencia.csv`."""
    return {r["metrica"]: r["rho_spearman"] for r in conv
            if r["rho_spearman"] is not None}


def _cambios(conv):
    """Rangos que se movieron 2 o más puestos; la métrica va etiquetada."""
    et = {"KS_KALINA": "KS", "PRCC_eta": "PRCC"}
    d = [f'{et.get(r["metrica"], r["metrica"])} {r["variable"]} '
         f'({r["rango_150"]} → {r["rango_300"]})'
         for r in conv if r["rango_150"] and r["rango_300"]
         and abs(r["rango_150"] - r["rango_300"]) >= 2]
    return ", ".join(d) if d else "ninguna variable cambia 2 o más posiciones"


def _reglas(cart):
    """Las hojas del árbol, tal como quedaron escritas en `m4_cart.txt`."""
    trozo = (cart.get("texto") or "").split("reglas en palabras:")[-1]
    lin = [l for l in trozo.splitlines() if l.startswith("- si ")]
    return lin or ["- (no hay árbol: faltan las dos clases)"]


def _doc(filas, rsa, pawn, prcc, cart, conv, top, chicos):
    res = resumen(filas)
    nk = res["conteos"].get("KALINA", 0)
    clases = ", ".join(f"{k} = {v}" for k, v in res["conteos"].most_common())
    k_r = [r for r in rsa if r["separacion"] == "KALINA"]
    k0 = next(r for r in k_r if r["variable"] == VARS10[0])
    rk = {r["variable"]: r for r in k_r}
    rho = _rho(conv)
    pj = sorted([r for r in pawn if r["salida"] == "eta"],
                key=lambda r: -(r["T_mediana"] or 0.0))[:3]
    ce = sorted([r for r in prcc if r["salida"] == "eta" and r["prcc"] is not None],
                key=lambda r: -abs(r["prcc"]))[:3]
    der = ", ".join(f'{v}: KS {nf(rk[v]["KS"])} y rango favorable '
                    f'[{gf(rk[v]["fav_p05"])}, {gf(rk[v]["fav_p95"])}]'
                    for v in DERIV)
    aviso = (f"Ningún grupo quedó por debajo de {N_MINIMO} puntos."
             if not chicos else
             f"**Aviso:** estos grupos quedaron con menos de {N_MINIMO} puntos "
             "y NO se amplió el muestreo por cuenta propia (el director decide):\n"
             + "\n".join(f"- `{c}`" for c in chicos))
    return f"""# REPORTE M4 — sensibilidad global con LHS (10 variables a la vez)
## 1. La pregunta
Moviendo **las 10 variables a la vez** dentro de un rango favorable y realista: **¿qué variables deciden que el ciclo sea KALINA?, ¿en qué rango hay que ponerlas? y ¿qué combinaciones dan KALINA con mayor η?**
## 2. Qué se hizo, en simple
- **Muestreo.** {res['n']} puntos con muestreo latino hipercubico (LHS, semilla 20261006): cada rango se divide en {res['n']} franjas y cae exactamente un punto en cada franja de cada variable, así ninguna zona de la caja queda sin explorar. La muestra quedó en `m4_muestra.csv` ANTES de correr.
- **Corrida.** Los {res['n']} puntos se resolvieron con el motor `teqp` y 5 procesos, con el piso de O2 de cada punto igual a su propia `T_sumidero`. Todo quedó en `m4_lhs.csv`.
- **Punto bueno (genuino).** Solo cuentan KALINA, CORREGIBLE e INVIABLE. Una fila que el solver cerró pero que el clasificador marca NO_CONVERGIO es un punto fijo espurio (N2) y es NO genuina en todo.
- **Análisis.** RSA (KS, valor p, IC95 % por bootstrap de 1000 remuestreos y rango favorable = percentiles 5–95) con cuatro separaciones; PAWN con 10 franjas; PRCC con rangos, residuos y prueba t; un árbol CART; la convergencia del ranking con los primeros 150 puntos; y el top-10.
## 3. Cuántos KALINA salieron
De **{res['n']}** puntos: **{nk} KALINA**. Conteos por clase: {clases}.
Puntos genuinos: {res['n_genuinos']}. Espurios N2 (`convergio=True` y NO_CONVERGIO): {res['n_N2']}. Fuera del rango confiable del motor de propiedades: {res['n_fuera']}.
## 4. Qué variables deciden KALINA y su rango favorable
Separación **KALINA vs el resto** (B = los {k0['n_B']} KALINA; B̄ = los {k0['n_Bbar']} demás), ordenada por KS. El rango favorable es donde viven los KALINA (percentiles 5–95 dentro de B):

{tabla_rsa(k_r)}

{aviso}
### 4.1 Las otras separaciones (misma caja)
**Genuino vs no genuino:**

{tabla_rsa([r for r in rsa if r["separacion"] == "converge"])}

**Cumple O2 vs no (entre genuinos):**

{tabla_rsa([r for r in rsa if r["separacion"] == "cumple_O2"])}

**Cumple O1 vs no (entre genuinos):**

{tabla_rsa([r for r in rsa if r["separacion"] == "cumple_O1"])}
## 5. Qué variables mueven η y en qué sentido
**PAWN** (sobre η de los genuinos con W_net > 0 y sobre D de los genuinos; cuanto más alto el índice, más cambia la distribución al fijar la variable):

{tabla_pawn(pawn)}

Las tres con más peso sobre η por PAWN: {", ".join(f'{r["variable"]} ({nf(r["T_mediana"])})' for r in pj)}.

**PRCC** (negativo = subir la variable baja η; el IC95 % que no cruza al cero indica que el efecto se distingue del ruido):

{tabla_prcc(prcc)}

Las de mayor |PRCC| sobre η: {", ".join(f'{r["variable"]} ({nf(r["prcc"])})' for r in ce)}.
## 6. Las reglas del árbol, en palabras
Clasificador CART (`max_depth=4`, `min_samples_leaf=5`, `random_state=0`) sobre las 10 variables, KALINA vs no KALINA. {cart["acc"]}.
{chr(10).join(_reglas(cart))}
## 7. Los diferenciales recomendados dentro de KALINA
Las tres variables derivadas, con su KS en la separación KALINA y su rango favorable (percentiles 5–95 dentro de los KALINA): {der}.
## 8. Los 10 mejores KALINA
Los {len(top)} KALINA de mayor η de la corrida:

{tabla_top(top)}
## 9. La convergencia
ρ de Spearman entre el ranking con los primeros 150 puntos y el de los {res['n']}: **KS (KALINA) = {nf(rho.get("KS_KALINA"), 4)}** y **PRCC(η) = {nf(rho.get("PRCC_eta"), 4)}**. Variables que cambian 2 o más posiciones: {_cambios(conv)}.
## 10. Los tiempos
{_tiempos(filas)}
## 11. La conclusión
El RSA de §4 dice qué variables separan KALINA del resto y en qué rango viven los KALINA; PAWN y PRCC de §5 dicen qué variables mueven η y en qué sentido; el árbol de §6 da reglas sí/no que se leen directo; y §7 da los diferenciales (dP, rP, dT_fs) recomendados dentro de KALINA. No se propone ningún valor nuevo: las tablas son insumos para que el director decida.
## 12. Lo que no se sabe
- Las diferencias de η menores que 0.4–0.7 pp no son concluyentes: es la banda de incertidumbre del modelo de propiedades (G4-01).
- Hay puntos fuera de rango (motor de propiedades sin respaldo experimental): {res['n_fuera']} de {res['n']}. Sus η hay que tomarlas con pinzas.
- Esto es una **caja favorable**, no todo el espacio: fuera de los rangos de `TASK_CONTEXT final_M4` no se dijo nada.
## 13. Qué sigue
M5 (búsqueda dirigida hacia KALINA con las variables que señala el RSA). El orden concreto lo decide el director.
"""


def generar(filas, rsa, pawn, prcc, cart, conv, top, chicos) -> None:
    (OUT / "REPORTE_M4.md").write_text(
        _doc(filas, rsa, pawn, prcc, cart, conv, top, chicos), encoding="utf-8")
    print("REPORTE_M4.md escrito", flush=True)


if __name__ == "__main__":
    raise SystemExit("Importar desde m4_analisis.py; la corrida es m4_analisis.py")
