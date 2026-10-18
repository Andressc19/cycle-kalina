# -*- coding: utf-8 -*-
"""Sens2 - p5_trazado: comprueba que cada cifra de las conclusiones sale de un CSV de resultados.

Lee `p5_conclusiones.csv` (columnas `afirmacion`, `evidencia` e `implicacion`), extrae los numeros y los compara
con un conjunto de referencia formado por todas las columnas numericas de los CSV de `resultados/2026-10-17_sens2_P1`
a `P4`, `resultados/2026-10-17_sens2_U1` y `resultados/2026-10-18_sens2_R1`, mas los valores de `p5_hechos.hechos()`.

Un numero queda `trazado = "si"` si su valor redondeado a sus decimales esta en el conjunto de referencia de esos
decimales (tolerancia exacta de redondeo) o si figura en `p5_trazado_permitidos.csv`. Un entero con |valor| < 10 y
0 decimales se marca `trivial`. El resto se marca `no`. El script solo informa: escribe `p5_trazado.csv` y
`p5_trazado.md`, imprime las mismas cifras y no corrige ningun texto.
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
from p5_hechos import hechos  # noqa: E402

CARPETAS = ("2026-10-17_sens2_P1", "2026-10-17_sens2_P2", "2026-10-17_sens2_P3",
            "2026-10-17_sens2_P4", "2026-10-17_sens2_U1", "2026-10-18_sens2_R1")
CAMPOS = ("afirmacion", "evidencia", "implicacion")
SIGNO = "\\-" + "\u2212"                             # guion ASCII y signo menos unicode, escapados para una clase
PATRON = re.compile(r"(?<![\w%s])([%s]?\d{1,3}(?: \d{3})+|[%s]?\d+(?:\.\d+)?)(?![\w])" % (SIGNO, SIGNO, SIGNO))
MOTIVO = "constante de diseno o limite del criterio, citada tal cual"
CONTEXTO = 20                                        # caracteres a cada lado del numero en el informe


def _decimales(txt):
    return len(txt.split(".")[1]) if "." in txt else 0


def _valor(txt):
    return float(txt.replace(" ", "").replace("\u2212", "-"))


def _agregar(ref, v, fuente):
    v = v[np.isfinite(v)]
    if v.size == 0:
        return
    for d in range(5):
        for arr in (np.round(v, d), np.round(np.abs(v), d), np.round(100.0 * v, d), np.round(100.0 * (1.0 - v), d)):
            for x in np.unique(arr):
                ref[d].setdefault(float(x), fuente)


def referencia():
    """dict[d] -> {valor_redondeado -> primera fuente "archivo:columna"} para d en 0..4."""
    ref = {d: {} for d in range(5)}
    for carpeta in CARPETAS:
        base = os.path.join(R, carpeta)
        for dp, _, fs in os.walk(base):
            for fn in sorted(fs):
                if not fn.endswith(".csv"):
                    continue
                ruta = os.path.join(dp, fn)
                try:
                    df = pd.read_csv(ruta)
                except Exception:
                    continue
                rel = os.path.relpath(ruta, base).replace("\\", "/")
                for col in df.columns:
                    if pd.api.types.is_numeric_dtype(df[col]):
                        _agregar(ref, df[col].to_numpy(dtype=float), "%s/%s:%s" % (carpeta, rel, col))
    vals = [float(x) for x in hechos().values() if isinstance(x, (int, float)) and not isinstance(x, bool)]
    _agregar(ref, np.array(vals, dtype=float), "p5_hechos:hechos()")
    return ref


def permitidos():
    p = os.path.join(D, "p5_trazado_permitidos.csv")
    if not os.path.exists(p):
        return {}
    d = pd.read_csv(p)
    return {float(v): str(m) for v, m in zip(d["valor"], d["motivo"])}


def extraer(texto, campo):
    out = []
    for m in PATRON.finditer(str(texto)):
        num = m.group(0)
        out.append((num, _decimales(num), _valor(num), campo, m.start(), m.end()))
    return out


def clasificar(dec, valor, ref, perm):
    if dec == 0 and valor == int(valor) and abs(valor) < 10:
        return "trivial", "trivial"
    d = min(dec, 4)
    clave = round(valor, d)
    if clave in ref[d]:
        return "si", ref[d][clave]
    if clave in perm:
        return "si", "permitido: %s" % perm[clave]
    return "no", ""


def _contexto(texto, ini, fin):
    a, b = max(0, ini - CONTEXTO), min(len(texto), fin + CONTEXTO)
    return texto[a:b].replace("\r", " ").replace("\n", " ").replace("|", "/")


def _informe(filas, tot, tra, tri, no, pct):
    with open(os.path.join(D, "p5_trazado.md"), "w", encoding="utf-8") as f:
        f.write("# Sens2 P5 - trazado de las cifras de las conclusiones\n\n")
        f.write("Cifras de `p5_conclusiones.csv` buscadas en los CSV de resultados y en `p5_trazado_permitidos.csv`.\n\n")
        f.write("- total de numeros: %d\n" % tot)
        f.write("- trazados: %d\n" % tra)
        f.write("- triviales: %d\n" % tri)
        f.write("- no trazados: %d\n" % no)
        f.write("- porcentaje de trazados (sobre el total): %.1f %%\n\n" % pct)
        f.write("## No trazados\n\n| id | campo | numero | contexto |\n|---|---|---|---|\n")
        for x in filas:
            if x["trazado"] == "no":
                f.write("| %s | %s | %s | %s |\n" % (x["id"], x["campo"], x["numero"], x["_ctx"]))


def main():
    base = pd.read_csv(os.path.join(D, "p5_conclusiones.csv"))
    ref, perm = referencia(), permitidos()
    filas = []
    for r in base.itertuples():
        for campo in CAMPOS:
            texto = str(getattr(r, campo))
            for num, dec, valor, camp, ini, fin in extraer(texto, campo):
                estado, fuente = clasificar(dec, valor, ref, perm)
                filas.append({"id": r.id, "campo": campo, "numero": num, "decimales": dec, "trazado": estado,
                              "fuente": fuente, "_ctx": _contexto(texto, ini, fin)})
    tot = len(filas)
    tra = sum(x["trazado"] == "si" for x in filas)
    tri = sum(x["trazado"] == "trivial" for x in filas)
    no = sum(x["trazado"] == "no" for x in filas)
    pct = (100.0 * tra / tot) if tot else 0.0
    cols = ["id", "campo", "numero", "decimales", "trazado", "fuente"]
    pd.DataFrame([{k: x[k] for k in cols} for x in filas]).to_csv(
        os.path.join(D, "p5_trazado.csv"), index=False, encoding="utf-8", lineterminator="\r\n")
    _informe(filas, tot, tra, tri, no, pct)
    print("total numeros: %d" % tot)
    print("trazados: %d" % tra)
    print("triviales: %d" % tri)
    print("no trazados: %d" % no)
    print("porcentaje de trazados: %.1f %%" % pct)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:                                    # es un informe: nunca falla la ejecucion
        print("ERROR: %s" % e)
    raise SystemExit(0)
