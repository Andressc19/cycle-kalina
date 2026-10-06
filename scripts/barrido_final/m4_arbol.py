"""M4 — CART (KALINA vs no), convergencia del ranking y top-10 (MATEMATICA §6.5-6.6).

`arbol()` ajusta `DecisionTreeClassifier(max_depth=4, min_samples_leaf=5,
random_state=0)` sobre las 10 variables con la clase `KALINA` vs el resto,
reporta la exactitud con validación cruzada de 5 particiones, exporta las
reglas con `export_text` a `m4_cart.txt` y las traduce a palabras.
`convergencia()` repite el KS del RSA-KALINA y el PRCC(η) con los primeros 150
puntos (`id_muestra < 150`) y compara los rankings con los de los 300 mediante
el ρ de Spearman. `top_kalina()` devuelve los 10 KALINA de mayor η.
"""
from __future__ import annotations

import numpy as np
from scipy.stats import spearmanr
from sklearn.metrics import accuracy_score
from sklearn.model_selection import cross_val_score
from sklearn.tree import (DecisionTreeClassifier, export_text)

from m4_datos import OUT, VARS10, VARS13
from m4_pawn_prcc import filas_prcc
from m4_rsa import ks_de

PARAMS = dict(max_depth=4, min_samples_leaf=5, random_state=0)
CCONV = ["metrica", "variable", "valor_150", "valor_300", "rango_150",
         "rango_300", "rho_spearman"]
CTOP = ["puesto", "id_muestra", "eta", "Wnet", "D", *VARS10]


def reglas_palabras(tree, names: list) -> list:
    """Recorre el árbol y devuelve una frase por hoja (KALINA o no KALINA)."""
    t, frases = tree.tree_, []

    def rec(node, cond):
        if t.feature[node] < 0:
            n = int(t.n_node_samples[node])
            val = t.value[node][0]
            frac = float(val[1] / val.sum()) if val.sum() else 0.0
            clase = "KALINA" if frac >= 0.5 else "no KALINA"
            regla = " y ".join(cond) if cond else "(sin condiciones)"
            frases.append(f"- si {regla} → **{clase}** (n = {n}, "
                          f"{100.0 * frac:.1f} % KALINA)")
            return
        v, um = names[t.feature[node]], t.threshold[node]
        rec(t.children_left[node], cond + [f"{v} <= {um:.4g}"])
        rec(t.children_right[node], cond + [f"{v} > {um:.4g}"])

    rec(0, [])
    return frases


def arbol(filas: list) -> dict:
    """Ajusta el árbol, escribe `m4_cart.txt` y devuelve tree/texto/exactitud."""
    X = np.array([[f[v] for v in VARS10] for f in filas], dtype=float)
    y = np.array([f["clasificacion"] == "KALINA" for f in filas])
    lineas = [f"puntos = {len(y)} · KALINA = {int(y.sum())} · "
              f"no KALINA = {int((~y).sum())}", f"parametros = {PARAMS}", ""]
    if len(set(y)) < 2:
        lineas.append("No hay las dos clases: el árbol no se ajusta.")
        texto = "\n".join(lineas) + "\n"
        (OUT / "m4_cart.txt").write_text(texto, encoding="utf-8")
        print("m4_cart.txt: sin las dos clases", flush=True)
        return dict(ok=False, texto=texto, tree=None,
                    acc="no calculada (una sola clase)")
    tree = DecisionTreeClassifier(**PARAMS).fit(X, y)
    if min(int(y.sum()), int((~y).sum())) >= 5 and len(y) >= 10:
        cv = cross_val_score(DecisionTreeClassifier(**PARAMS), X, y, cv=5)
        acc = (f"exactitud CV (5 particiones): media = {cv.mean():.4f} · "
               f"por particion = {[round(float(a), 4) for a in cv]}")
    else:
        acc = "exactitud CV (5 particiones): NO CALCULADA (muestra pequeña)"
    lineas += [acc,
               f"exactitud in-sample = {accuracy_score(y, tree.predict(X)):.4f}",
               "", "reglas (export_text):",
               export_text(tree, feature_names=list(VARS10), decimals=4), "",
               "reglas en palabras:"]
    lineas += reglas_palabras(tree, list(VARS10))
    texto = "\n".join(lineas) + "\n"
    (OUT / "m4_cart.txt").write_text(texto, encoding="utf-8")
    print("m4_cart.txt escrito", flush=True)
    return dict(ok=True, texto=texto, tree=tree, acc=acc, X=X, y=y)


def _rho(a: list, b: list):
    p = [(x, y) for x, y in zip(a, b) if x is not None and y is not None]
    if len(p) < 3:
        return None
    return float(spearmanr([x for x, _ in p], [y for _, y in p]).correlation)


def _rangos(vals: list):
    """Rango 1 = valor de mayor magnitud (KS mayor, |PRCC| mayor)."""
    idx = [i for i, v in enumerate(vals) if v is not None]
    r = [None] * len(vals)
    for puesto, i in enumerate(sorted(idx, key=lambda i: -abs(vals[i])), 1):
        r[i] = puesto
    return r


def convergencia(filas: list) -> list:
    """KS (RSA KALINA) y PRCC(η) con los primeros 150 vs los 300, ρ de Spearman."""
    sub = [f for f in filas if f["id_muestra"] is not None and f["id_muestra"] < 150]
    p300 = {r["variable"]: r["prcc"] for r in filas_prcc(filas) if r["salida"] == "eta"}
    p150 = {r["variable"]: r["prcc"] for r in filas_prcc(sub) if r["salida"] == "eta"}
    bloques = []
    pares = (("KS_KALINA", VARS13,
              [ks_de(sub, "KALINA", v) for v in VARS13],
              [ks_de(filas, "KALINA", v) for v in VARS13]),
             ("PRCC_eta", VARS10, [p150.get(v) for v in VARS10],
              [p300.get(v) for v in VARS10]))
    for metrica, vars_, v150, v300 in pares:
        rho, r150, r300 = _rho(v150, v300), _rangos(v150), _rangos(v300)
        for v, a, b, ra, rb in zip(vars_, v150, v300, r150, r300):
            bloques.append(dict(metrica=metrica, variable=v, valor_150=a,
                                valor_300=b, rango_150=ra, rango_300=rb,
                                rho_spearman=rho))
    return bloques


def top_kalina(filas: list) -> list:
    """Los 10 KALINA de mayor η, con sus 10 variables."""
    kal = sorted([f for f in filas if f["clasificacion"] == "KALINA"
                  and f["eta"] is not None], key=lambda f: -f["eta"])[:10]
    return [dict(puesto=i, id_muestra=f["id_muestra"], eta=f["eta"],
                 Wnet=f["Wnet"], D=f["D"], **{v: f[v] for v in VARS10})
            for i, f in enumerate(kal, 1)]
