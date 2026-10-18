# -*- coding: utf-8 -*-
"""Sens2 A5 - make_supuestos: escribe `sens2_supuestos.json` con los supuestos y umbrales del analisis.

Los valores se LEEN de los modulos que los definen (no se copian a mano). Los que son decisiones del
plan llevan `donde: docs/PLAN_SENS2_MEJORA.md`. Cada entrada tiene `valor` y `donde`.
"""
import json
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
sys.path.insert(0, AQUI)
sys.path.insert(0, os.path.join(RAIZ, "scripts", "sens1"))

import p3_comun as P3  # noqa: E402
import r1_filtro as RF  # noqa: E402
import r2_eficiencias as RE  # noqa: E402
import r2_vecinos as RV  # noqa: E402
import u1_analisis as UA  # noqa: E402
import u1_puntos as UP  # noqa: E402

M = "scripts/sens2/%s.py"
PLAN = "docs/PLAN_SENS2_MEJORA.md"
SALIDA = os.path.join(AQUI, "sens2_supuestos.json")


def supuestos():
    """Diccionario {clave: {valor, donde}} leido de los modulos y del plan."""
    s = {}

    def pon(clave, valor, donde):
        s[clave] = {"valor": valor, "donde": donde}

    pon("semilla", P3.SEMILLA, M % "p3_comun")
    pon("n_boot", P3.N_BOOT, M % "p3_comun")
    pon("n_perm", P3.N_PERM, M % "p3_comun")
    pon("tolerancias_u1", UP.TOL, M % "u1_puntos")
    pon("escenarios_u1", UP.ESCENARIOS, M % "u1_puntos")
    pon("cercania_r1", RF.CERCANO, M % "r1_filtro")
    pon("cobertura_r1", RF.COBERTURA, M % "r1_filtro")
    pon("tolerancia_eficiencias_r2", RE.TOL_EF, M % "r2_eficiencias")
    pon("k_vecinos", RV.K, M % "r2_vecinos")
    pon("banda_modelo_pp", UA.BANDA_MODELO, M % "u1_analisis")
    pon("semilla_f1", 20261018, PLAN)
    pon("q_fdr", 0.05, PLAN)
    pon("n_permutaciones_f1", 500, PLAN)
    pon("n_min_confianza", 30, PLAN)
    pon("auc_minimo", 0.8, PLAN)
    pon("procedencia", {
        "u1_808_puntos": "corridos por el director con u1_corrida.py (OpenCode no arrancó)",
        "r1": "OpenCode con vigilante; r2: director"}, PLAN)
    return s


def main():
    s = supuestos()
    with open(SALIDA, "w", encoding="utf-8") as fh:
        json.dump(s, fh, ensure_ascii=False, indent=2, sort_keys=True)
        fh.write("\n")
    print("escrito:", SALIDA, "| claves:", len(s))
    for clave in sorted(s):
        print("  %-28s -> %s" % (clave, s[clave]["donde"]))


if __name__ == "__main__":
    main()
