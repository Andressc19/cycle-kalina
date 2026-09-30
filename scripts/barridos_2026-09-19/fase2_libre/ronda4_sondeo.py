"""Fase 2, ronda 4 — registro del SONDEO previo a la campana (tarea
2026-09-28-fase2-ronda4-campana-3h).

Antes de fijar la escalera de P_baja hubo que medir de verdad donde esta la
frontera O2 con las efectividades ESTRICTAS de esta ronda (eps_hrvg=eps_reg=0.80,
eps_cond <= 0.85, x_b >= 0.40, ancla 470.0/300.032917/303.55 K, TeqpAdapter):
con P_baja en el rango viejo (~400-800 kPa) TODO salia CORREGIBLE, asi que la
campana necesitaba saber hasta donde stretches P_baja. Este script corre esos
puntos de sondeo y los REGISTRA en busqueda_libre_v2.csv con el mismo esquema
de 19 columnas (append), para que queden trazados como cualquier otro punto y
para que la campana no los vuelva a calcular (el anti-duplicado por 8-tuplo
los-descarta solo).

Salida: APPEND a busqueda_libre_v2.csv. NO crea CSVs nuevos. NO toca src/.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from ronda4_campana import correr                      # noqa: E402
from ronda4_columnas import cargar_r2, combo           # noqa: E402

# (P_baja, x_b, eps_cond) con P_alta=3000 salvo la ultima; base de las rondas
# 1-3 en eta_t/eta_p, y eps_hrvg=eps_reg=0.80 (centro del rango [0.75, 0.85]
# permitido en esta ronda).
SONDEO = ((1000., 0.40, 0.85), (1000., 0.45, 0.85), (1000., 0.50, 0.85),
          (1400., 0.40, 0.85), (1400., 0.45, 0.85), (1400., 0.50, 0.85),
          (1700., 0.50, 0.80), (2100., 0.50, 0.80), (2500., 0.50, 0.80),
          (2700., 0.50, 0.80), (2500., 0.50, 0.75), (2700., 0.50, 0.75),
          (650., 0.40, 0.85), (800., 0.40, 0.85), (1000., 0.45, 0.85),
          (1400., 0.45, 0.80), (2700., 0.50, 0.75), (1900., 0.40, 0.75))
P_ALTA_3300 = 2700., 0.50, 0.75        # unico punto con P_alta=3300


def main() -> None:
    r2 = cargar_r2()
    base = dict(r2.BASE, eps_hrvg=0.80, eps_reg=0.80)
    cand = [combo(dict(base, P_alta=3000., x_b=xb, eps_cond=ec, eta_t=0.85,
                       eta_p=0.75), pb) for pb, xb, ec in SONDEO]
    cand.append(combo(dict(base, P_alta=3300., x_b=P_ALTA_3300[1],
                           eps_cond=P_ALTA_3300[2], eta_t=0.85, eta_p=0.75),
                      P_ALTA_3300[0]))
    probadas = r2.leer_probadas()
    unicas = {r2.tupla(c): c for c in cand}
    nuevas = [c for t, c in unicas.items() if t not in probadas]
    print(f"[sondeo] candidatas: {len(cand)} | repetidas dentro de la tanda: "
          f"{len(cand) - len(unicas)} | ya probadas: "
          f"{len(unicas) - len(nuevas)} | nuevas: {len(nuevas)}", flush=True)
    correr(nuevas, "sondeo", 1200.0)


if __name__ == "__main__":
    main()
