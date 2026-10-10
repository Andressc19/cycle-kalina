# -*- coding: utf-8 -*-
"""A5 · Verifica el tablero: tamaño, JSON embebido, KPIs de 3 bloques y anglicismos."""
import json, os, re, sys
import pandas as pd

SALIDA = "analisis_final/06_tablero/tablero_kalina.html"
CANONICA = "analisis_final/01_datos/todos_los_puntos.csv"
BLOQUES_CSV = "analisis_final/00_inventario/bloques.csv"


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

    # 5. C1: llamada a resize() en manejador de cambio de pestaña.
    print("[5] Verificación C1 — resize() en cambio de pestaña:")
    i = html.find("function activarSec(")
    if i >= 0 and "resize()" in html[i:i + 800]:
        print("    OK: se encontró llamada a resize() en activarSec")
    else:
        print("    FALLA: no se encontró resize() en activarSec")
    # Toda función usada por los manejadores tiene que estar definida en el HTML final
    # (así se detecta un .js que el armado no incluyó).
    for fn in ("pinta", "activarSec", "cfgDisp", "cfgResumen", "cfgBloqueos"):
        ok = re.search(r"function\s+" + fn + r"\s*\(", html) is not None
        print(f"    {'OK' if ok else 'FALLA'}: función {fn} definida en el HTML")

    # 6. C2: 5 opciones del selector de bloque.
    print("[6] Primeras 5 opciones del selector de bloque (value · texto):")
    opts = re.findall(r'<option value="([^"]+)">([^<]+)</option>', html)
    bloque_opts = [o for o in opts if o[0].startswith("B")]
    for v, t in bloque_opts[:5]:
        print(f"    {v} · {t}")

    # 7. C2: DESCRIPCION_BLOQUE cubre todos los bloque_director.
    print("[7] Verificación C2 — cobertura de DESCRIPCION_BLOQUE:")
    blo = pd.read_csv(BLOQUES_CSV)
    blo = blo[blo["bloque_director"] != "BX"]
    bloques = blo["bloque_director"].unique().tolist()
    # Cargar DESCRIPCION_BLOQUE desde a5_tablero.py (simplificado: extraer del JS embebido)
    # Como el JS no tiene el dict, lo importamos del módulo
    sys.path.insert(0, "scripts/analisis_final")
    from a5_tablero import DESCRIPCION_BLOQUE
    sin_desc = [b for b in bloques if not any(b.startswith(p.rstrip("-")) for p in DESCRIPCION_BLOQUE)]
    if not sin_desc:
        print(f"    OK: todos los {len(bloques)} bloques tienen descripción")
    else:
        print(f"    FALLA: {len(sin_desc)} bloques sin descripción: {sin_desc[:10]}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
