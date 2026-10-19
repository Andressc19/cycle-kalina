# -*- coding: utf-8 -*-
"""Sens2 A5 - make_sens2: orquestador; una orden corre los pasos de Sensibilidad 2.

Pasos base (siempre) y, con --todo, los de P1 a P4, U1 y R1/R2 antes de ellos. Cada paso es un
script de `scripts/sens2/`; si no existe se salta con aviso; si falla, se detiene con ese codigo.
Al final de los pasos base corre las pruebas (`pruebas`) salvo --sin-pruebas. Escribe un registro
JSON con el estado, los segundos y el codigo de cada paso, el commit, las versiones y los sha256
de los dos CSV de entrada.
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import time

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
SCRIPTS = os.path.join(RAIZ, "scripts", "sens2")
REGISTRO_DEF = os.path.join("resultados", "2026-10-18_sens2_F1", "make_sens2_registro.json")
PRUEBAS = "pruebas"
ARCHIVOS = ["tests/test_sens2_libro.py", "tests/test_sens2_cifras.py", "tests/test_sens2_r1.py", "tests/test_sens2_docs.py"]
HUELLAS = ["resultados/2026-10-17_sens2_P2/p2_dataset_dedup.csv",
           "resultados/2026-10-17_sens2_U1/u1_filas.csv"]

TODO = ["p1_dataset", "p1_existencia", "p1_fronteras", "p1_reglas", "p2_comparacion",
        "p2_violaciones", "p2_distancia", "p2_robustez", "p3_indices", "p3_elasticidad",
        "p3_interaccion", "p3_resumen", "p4_envolventes", "p4_dependencias", "p4_bandas",
        "u1_analisis", "r1_filtro", "r1_contraste", "r2_eficiencias", "r2_vecinos", "r2_agregado"]
BASE = ["p6_mO2", "p6_nulo", "p6_nc", "p6_pareado", "p6_pareado_dist", "p6_equipos_diseno", "p6_equipos_ic", "p6_equipos_kw",
        "p6_ciclo_T", "p6_potencia_u1", "p6_fronteras_ic", "p6_superficies_cv", "p6_m5_lhs", "p6_calibra_regla", "p6_m5_pruebas", "p6_pisos25", "p6_reintento_nc", "p6_dens", "p6_sim", "p6_opt_T", "p5_generar", "p5_trazado", "p5_trazado_fuente", "p5_cifras_check",
        "p5_cifras_check_c", "s2_construir", "p5_globales", "docs_sync", "s2_verificar", "s2_informe", "p5_lint_texto", "p5_docs_check", "s2_figuras", "s2_informe_pdf"]
ORDEN = TODO + BASE + [PRUEBAS]


def entorno():
    e = dict(os.environ)
    e["PYTHONPATH"] = os.path.join("scripts", "sens2")
    e["PYTHONIOENCODING"] = "utf-8"
    return e


def sha256(ruta):
    h = hashlib.sha256()
    with open(os.path.join(RAIZ, ruta), "rb") as fh:
        for bloque in iter(lambda: fh.read(1 << 20), b""):
            h.update(bloque)
    return h.hexdigest()


def commit():
    try:
        r = subprocess.run(["git", "rev-parse", "HEAD"], cwd=RAIZ, capture_output=True, text=True)
        return r.stdout.strip() if r.returncode == 0 else None
    except OSError:
        return None


def versiones():
    import numpy
    import openpyxl
    import pandas
    import scipy
    return {"python": sys.version.split()[0], "numpy": numpy.__version__,
            "pandas": pandas.__version__, "scipy": scipy.__version__,
            "openpyxl": openpyxl.__version__}


def correr(nombre):
    """Un paso normal: (registro, codigo de salida)."""
    ruta = os.path.join(SCRIPTS, nombre + ".py")
    if not os.path.exists(ruta):
        print("[%s] no existe todavia (se salta)" % nombre)
        return {"nombre": nombre, "estado": "ausente", "segundos": 0.0, "codigo": None}, 0
    print("[%s] ..." % nombre)
    t = time.time()
    r = subprocess.run([sys.executable, ruta], cwd=RAIZ, env=entorno())
    seg = round(time.time() - t, 2)
    estado = "ok" if r.returncode == 0 else "fallo"
    print("[%s] %s (%.2f s)" % (nombre, estado, seg))
    return {"nombre": nombre, "estado": estado, "segundos": seg, "codigo": r.returncode}, r.returncode


def correr_pruebas():
    """Paso `pruebas`: pytest -q sobre los tres archivos de Sensibilidad 2."""
    print("[%s] ..." % PRUEBAS)
    t = time.time()
    r = subprocess.run([sys.executable, "-m", "pytest", "-q"] + ARCHIVOS + ["-p", "no:cacheprovider"],
                       cwd=RAIZ, env=entorno())
    seg = round(time.time() - t, 2)
    print("[%s] %s (%.2f s)" % (PRUEBAS, "ok" if r.returncode == 0 else "fallo", seg))
    return {"nombre": PRUEBAS, "estado": "ok" if r.returncode == 0 else "fallo",
            "segundos": seg, "codigo": r.returncode}, r.returncode


def seleccion(args):
    if args.solo:
        faltan = [n for n in args.solo if n not in ORDEN]
        if faltan:
            raise SystemExit("pasos desconocidos: %s" % faltan)
        return [n for n in ORDEN if n in args.solo]
    pasos = list(TODO) + list(BASE) if args.todo else list(BASE)
    if args.desde:
        if args.desde not in pasos:
            raise SystemExit("--desde desconocido: %s" % args.desde)
        pasos = pasos[pasos.index(args.desde):]
    if not args.sin_pruebas:
        pasos = pasos + [PRUEBAS]
    return pasos


def main():
    p = argparse.ArgumentParser(description="Orquestador de Sensibilidad 2.")
    p.add_argument("--lista", action="store_true", help="imprime los pasos y termina")
    p.add_argument("--solo", nargs="+", metavar="NOMBRE", help="corre solo estos pasos")
    p.add_argument("--desde", metavar="NOMBRE", help="corre desde este paso")
    p.add_argument("--todo", action="store_true", help="incluye P1 a P4, U1 y R1/R2")
    p.add_argument("--sin-pruebas", action="store_true", help="no corre el paso pruebas")
    p.add_argument("--registro", default=REGISTRO_DEF, help="ruta del JSON de registro")
    args = p.parse_args()

    if args.lista:
        print("pasos (--todo antes de los base; pruebas al final):")
        for n in ORDEN:
            marca = "base" if n in BASE else ("todo" if n in TODO else "pruebas")
            print("  %-18s (%s)" % (n, marca))
        return 0

    pasos = seleccion(args)
    print("pasos a correr:", ", ".join(pasos) if pasos else "(ninguno)")
    registro = {"commit": commit(), "versiones": versiones(),
                "huellas": {h: sha256(h) for h in HUELLAS}, "pasos": []}
    codigo_final = 0
    for nombre in pasos:
        fila, codigo = correr_pruebas() if nombre == PRUEBAS else correr(nombre)
        registro["pasos"].append(fila)
        if codigo:
            codigo_final = codigo
            break
    ruta = args.registro if os.path.isabs(args.registro) else os.path.join(RAIZ, args.registro)
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with open(ruta, "w", encoding="utf-8") as fh:
        json.dump(registro, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print("registro:", ruta)
    return codigo_final


if __name__ == "__main__":
    sys.exit(main())
