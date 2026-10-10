# -*- coding: utf-8 -*-
"""A5 · Verifica el tablero: tamaño, JSON embebido, KPIs de 3 bloques y anglicismos."""
import json
import os
import re
import sys

import pandas as pd

SALIDA = "analisis_final/06_tablero/tablero_kalina.html"
CANONICA = "analisis_final/01_datos/todos_los_puntos.csv"


def es_verdadero(v):
    if isinstance(v, str):
        return v.strip().lower() in ("true", "1", "verdadero", "si", "sí")
    try:
        if pd.isna(v):
            return False
    except (TypeError, ValueError):
        return False
    return bool(v)


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

    # 1. Existe y tamaño.
    if not os.path.exists(SALIDA):
        print("FALLA: no existe", SALIDA)
        return 1
    mb = os.path.getsize(SALIDA) / (1024 * 1024)
    print(f"[1] HTML existe: {SALIDA}")
    print(f"[1] Tamaño: {mb:.2f} MB (< 15 MB: {'OK' if mb < 15 else 'FALLA'})")

    with open(SALIDA, encoding="utf-8") as f:
        html = f.read()

    # 2. Extrae el JSON embebido y comprueba PUNTOS.
    m = re.search(r"const DATOS\s*=\s*(.+?);\s*</script>", html, re.S)
    if not m:
        print("[2] FALLA: no se encontró el JSON embebido")
        return 1
    datos = json.loads(m.group(1))
    n_puntos = len(datos["PUNTOS"])
    df = pd.read_csv(CANONICA)
    n_esperado = int((df["id_caso"] != "KF-M08").sum())
    print(f"[2] PUNTOS en HTML: {n_puntos}")
    print(f"[2] Filas canónicas sin KF-M08: {n_esperado} "
          f"({'OK' if n_puntos == n_esperado else 'FALLA'})")
    vacios = [p["id_punto"] for p in datos["PUNTOS"]
              if p.get("bloque_director") in (None, "")]
    print(f"[2] PUNTOS con bloque_director vacío: {len(vacios)} "
          f"({'OK' if not vacios else 'FALLA ' + str(vacios[:5])})")

    # 3. KPIs recalculados en Python para B06, B07 y B10.
    print("[3] KPIs que debe mostrar el navegador (recalculados en Python):")
    for bloque in ("B06", "B07", "B10"):
        g = df[df["bloque_director"] == bloque]
        corridas = len(g)
        genuinas = int(g["genuino"].map(es_verdadero).sum())
        kalina = int(g["clase_trazo"].eq("KALINA").sum())
        conf = int(g["kalina_confiable"].map(es_verdadero).sum())
        print(f"    {bloque}: corridas={corridas} genuinas={genuinas} "
              f"KALINA={kalina} KALINA_confiables={conf}")

    # 4. Anglicismos de interfaz.
    print("[4] Palabras de interfaz en inglés encontradas en el HTML:")
    halladas = [w for w in ("Filter", "Download", "Show", "Page") if w in html]
    print("    " + (", ".join(halladas) if halladas else "ninguna"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
