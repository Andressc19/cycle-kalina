# -*- coding: utf-8 -*-
"""A3 · Verifica que cada figura del catálogo tenga PNG, SVG y pie completo."""
import glob
import json
import os

import codigos

RAIZ = "analisis_final/03_figuras"
CATALOGO = ["FIG-G01", "FIG-G02", "FIG-M09-01", "FIG-M02-01", "FIG-M02-02a", "FIG-M02-02b",
            "FIG-M02R-n1", "FIG-M02R-n2a", "FIG-M02R-n2b", "FIG-M02R-n3", "FIG-M02S-01",
            "FIG-M03-01", "FIG-M03-02", "FIG-M03-03", "FIG-M03-04", "FIG-M04-01",
            "FIG-M04-02", "FIG-M04-03", "FIG-M04-04", "FIG-M04c-01", "FIG-M05-S1",
            "FIG-M05-S2", "FIG-M05-S3", "FIG-M05-S4", "FIG-M05-S5", "FIG-M05c-01",
            "FIG-M06-01", "FIG-M07-01", "FIG-M10-01", "FIG-M10-02"]
CLAVES = ("Datos fijos", "Filtro", "n =", "Fuente")
CLAVES_SINTESIS = ("Filtro", "n =", "Fuente")   # síntesis: cada fila/línea trae sus datos


def main():
    fallas = 0
    for fid in CATALOGO:
        pngs = glob.glob(f"{RAIZ}/*/Figura_{codigos.figura(fid)}_*.png")    # nombre nuevo
        if not pngs:
            print(f"FALTA  {fid}: no hay PNG"); fallas += 1; continue
        base = pngs[0][:-4]
        svg, pie = os.path.exists(base + ".svg"), base + ".pie.md"
        texto = open(pie, encoding="utf-8").read() if os.path.exists(pie) else ""
        sintesis = fid in ("FIG-G01", "FIG-G02", "FIG-M09-01", "FIG-M02S-01",
                           "FIG-M06-01", "FIG-M07-01")
        claves = CLAVES_SINTESIS if sintesis else CLAVES
        sin_clave = [k for k in claves if k not in texto]
        oat = "Punto base" in texto
        if not svg or not texto or (sin_clave and not (oat and sin_clave == ["Datos fijos"])):
            print(f"FALTA  {fid}: svg={svg} pie={bool(texto)} faltan={sin_clave}"); fallas += 1
        else:
            extra = ""
            js = base + "_clases.json"
            if os.path.exists(js):
                extra = " · " + json.dumps(json.load(open(js, encoding="utf-8")),
                                           ensure_ascii=False)
            print(f"OK     {fid}: {os.path.basename(base)}{extra}")
    print(f"\n{len(CATALOGO) - fallas} de {len(CATALOGO)} figuras completas; fallas = {fallas}")
    return 1 if fallas else 0


if __name__ == "__main__":
    raise SystemExit(main())
