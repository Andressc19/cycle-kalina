# -*- coding: utf-8 -*-
"""Sens2 - p5_trazado_fuente: trazado de las cifras de cada conclusion contra SUS fuentes citadas (con poder).

`p5_trazado.py` compara con todos los CSV y no discrimina (un numero inventado de 2 decimales se traza el 100 % de las veces).
Aqui cada conclusion solo se compara con los CSV que cita en su columna `fuente` (mas los valores de `p5_hechos` y los
permitidos). Se escribe el porcentaje trazado, el poder del control negativo con la misma restriccion (cifras inventadas que
se trazarian) y la lista de lo no trazado, que son cifras escritas a mano sin respaldo directo en la fuente citada.
Salidas: p5_trazado_fuente.csv y p5_trazado_fuente.md. Solo informa; sale siempre con codigo 0.
"""
import os
import re
import sys

import numpy as np
import pandas as pd

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
R = os.path.join(RAIZ, "resultados")
D = os.path.join(R, "2026-10-17_sens2_P5")
sys.path.insert(0, AQUI)
import p5_trazado as T  # noqa: E402
from p5_hechos import hechos  # noqa: E402

P = {k: os.path.join(R, v) for k, v in (("P1", "2026-10-17_sens2_P1"), ("P2", "2026-10-17_sens2_P2"), ("P3", "2026-10-17_sens2_P3"),
                                        ("P4", "2026-10-17_sens2_P4"), ("U1", "2026-10-17_sens2_U1"), ("R1", "2026-10-18_sens2_R1"),
                                        ("F1", "2026-10-18_sens2_F1"), ("P5", "2026-10-17_sens2_P5"))}
HOJAS = {"F1 Margenes": ["P1:", "P2:p2_dataset_dedup"], "F4 Regenerador vs T_fuente": ["P4:", "P2:p2_dataset_dedup"],
         "F5 Superficies": ["P2:p2_dataset_dedup"], "F5 Incertidumbre": ["U1:"], "F4 Ciclo": ["F1:p6_ciclo"], "F3 Pisos 25 kPa": ["F1:p6_pisos25", "F1:p6_reintento_nc"], "F4 Equipos por kW": ["F1:p6_equipos_kw"],
         "Revisi": ["P2:p2_dataset_dedup", "U1:"], "p1 dataset": ["P1:p1_dataset"]}


def archivos(fuente):
    """Lista de CSV que cita una conclusion (por nombre de archivo, por hoja o por carpeta)."""
    out = set()
    todos = {}
    for k, base in P.items():
        for dp, _, fs in os.walk(base):
            for fn in fs:
                if fn.endswith(".csv"):
                    todos.setdefault(fn, []).append(os.path.join(dp, fn))
    for tok in re.findall(r"[\w\.]+\.(?:csv|md)", fuente):
        stem = tok.rsplit(".", 1)[0]
        for fn, rutas in todos.items():
            if fn == stem + ".csv" or (tok.endswith(".md") and fn.startswith(stem)):
                out.update(rutas)
    for clave, pats in HOJAS.items():
        if clave in fuente:
            for p in pats:
                carp, pref = p.split(":")
                for fn, rutas in todos.items():
                    for r in rutas:
                        if r.startswith(P[carp]) and fn.startswith(pref):
                            out.add(r)
    return sorted(out)


def referencia(rutas, extra):
    ref = {d: {} for d in range(5)}
    for ruta in rutas:
        try:
            df = pd.read_csv(ruta)
        except Exception:
            continue
        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                T._agregar(ref, df[col].to_numpy(dtype=float), os.path.basename(ruta) + ":" + col)
    T._agregar(ref, extra, "p5_hechos")
    return ref


def main():
    base = pd.read_csv(os.path.join(D, "p5_conclusiones.csv"))
    perm = T.permitidos()
    hv = np.array([float(x) for x in hechos().values() if isinstance(x, (int, float)) and not isinstance(x, bool)])
    filas, refs = [], {}
    for r in base.itertuples():
        rutas = archivos(str(r.fuente))
        refs[r.id] = referencia(rutas, hv)
        for campo in T.CAMPOS:
            texto = str(getattr(r, campo))
            for num, dec, valor, _, ini, fin in T.extraer(texto, campo):
                est, fte = T.clasificar(dec, valor, refs[r.id], perm)
                filas.append({"id": r.id, "campo": campo, "numero": num, "trazado": est, "fuente": fte, "n_archivos": len(rutas),
                              "_ctx": T._contexto(texto, ini, fin)})
    rng = np.random.default_rng(20261018)
    ids = list(refs)
    inv = [(round(float(rng.uniform(0.01, 99.99)), 2), ids[int(rng.integers(0, len(ids)))]) for _ in range(300)]
    poder = 100.0 * float(np.mean([T.clasificar(2, v, refs[i], perm)[0] == "si" for v, i in inv]))
    pod = {}
    for i in ids:
        v = [round(float(rng.uniform(0.01, 99.99)), 2) for _ in range(200)]
        pod[i] = 100.0 * float(np.mean([T.clasificar(2, x, refs[i], perm)[0] == "si" for x in v]))
    tot = len(filas)
    tra = sum(x["trazado"] == "si" for x in filas)
    tri = sum(x["trazado"] == "trivial" for x in filas)
    no = [x for x in filas if x["trazado"] == "no"]
    cols = ["id", "campo", "numero", "trazado", "fuente", "n_archivos"]
    pd.DataFrame([{k: x[k] for k in cols} for x in filas]).to_csv(os.path.join(D, "p5_trazado_fuente.csv"), index=False, encoding="utf-8", lineterminator="\r\n")
    md = ["# Sens2 P5 - trazado de las cifras contra las fuentes citadas por cada conclusion", "",
          "Cada cifra se busca solo en los CSV de la columna `fuente` de su conclusion (y en los valores de `p5_hechos`, que alimentan los marcadores, y en `p5_trazado_permitidos.csv`).", "",
          "- total de numeros: %d" % tot, "- trazados contra su fuente: %d (%.1f %%)" % (tra, 100.0 * tra / max(tot, 1)), "- triviales: %d" % tri,
          "- no trazados (escritos a mano sin respaldo directo en la fuente citada): %d (%.1f %%)" % (len(no), 100.0 * len(no) / max(tot, 1)),
          "- poder del control: una cifra inventada de dos decimales se habria trazado en el %.1f %% de los casos con esta restriccion (con todos los CSV: 100 %%)." % poder, "",
          "Los no trazados no son necesariamente erroneos (rangos redondeados, cifras de la literatura, constantes de diseno), pero no tienen respaldo automatico: "
          "las mas importantes se vigilan con `p5_cifras_check*.py`.", "", "## No trazados", "", "| id | campo | numero | contexto |", "|---|---|---|---|"]
    md += ["| %s | %s | %s | %s |" % (x["id"], x["campo"], x["numero"], x["_ctx"]) for x in no]
    md += ["", "## Poder por conclusion", "", "Porcentaje de cifras inventadas de dos decimales que se trazarian contra las fuentes de esa conclusion (200 por conclusion, semilla 20261018). "
           "Arriba del 80 % el trazado de esa conclusion es poco informativo y su respaldo real son los controles independientes.", "", "| id | poder (%) | trazado poco informativo |", "|---|---|---|"]
    md += ["| %s | %.0f | %s |" % (i, pod[i], "si" if pod[i] > 80 else "no") for i in ids]
    with open(os.path.join(D, "p5_trazado_fuente.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(md) + "\n")
    print("numeros %d | trazados %d | triviales %d | no trazados %d | poder %.1f %% | conclusiones con poder > 80 %%: %d de %d" % (
        tot, tra, tri, len(no), poder, sum(v > 80 for v in pod.values()), len(pod)))
    return len(no)


if __name__ == "__main__":
    # compuerta: sale con codigo 1 si queda alguna cifra sin respaldo en la fuente citada (o si el script falla)
    try:
        raise SystemExit(1 if main() else 0)
    except SystemExit:
        raise
    except Exception as e:
        print("ERROR: %s" % e)
        raise SystemExit(1)
