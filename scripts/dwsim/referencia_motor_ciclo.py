"""Referencia del motor del proyecto (IAPWS G4-01) para los puntos (a)-(d) del
ciclo NH3-H2O, via la interfaz publica `src.properties.AmmoniaWaterAdapter`.

Ejecutar con el .venv del proyecto:  .venv/Scripts/python scripts/dwsim/referencia_motor_ciclo.py
Escribe resultados/2026-10-03_dwsim_paquetes/referencia_motor.json

Unidades de la interfaz canonica (ver src/properties/adapter.py): P en kPa, T en K,
h en kJ/kg, s en kJ/kg-K, x = fraccion MASICA de NH3. P_baja = 273.55 kPa,
P_alta = 1500 kPa, x_b = 0.55 masica, T2 = 369 K, T9 = 287 K (caso Elsayed 2013).
"""
from __future__ import annotations

import json
import os
import sys
import time

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO)
OUT = os.path.join(REPO, "resultados", "2026-10-03_dwsim_paquetes")

from src.properties.ammonia_water_adapter import AmmoniaWaterAdapter  # noqa: E402
from src.properties.adapter import PropertyRangeError  # noqa: E402

M_NH3, M_H2O = 17.03052, 18.015268          # g/mol (guia IAPWS G4-01)
P_BAJA, P_ALTA, W_B, T2 = 273.55, 1500.0, 0.55, 369.0
T_REFDH = 300.0

# --- referencia de las Tablas 7 y 8 (guia IAPWS G4-01, valores publicados) -----
TABLA7 = [  # x_L molar, T [K] -> p_bub [MPa], x_v molar
    (0.2, 300.0, 0.040710, 0.9360),
    (0.4, 400.0, 2.5545, 0.9363),
    (0.6, 500.0, 16.698, 0.7844),
]
TABLA8 = [  # x_v molar, T [K] -> p_dew [MPa], x_L molar
    (0.2, 300.0, 0.00437062, 0.010672),
    (0.4, 400.0, 0.394694, 0.051541),
    (0.6, 500.0, 6.52607, 0.22135),
]


def molar_a_masica(x):
    """x molar de NH3 -> w masica de NH3 (la interfaz usa w)."""
    return x * M_NH3 / (x * M_NH3 + (1.0 - x) * M_H2O)


def masica_a_molar(w):
    """w masica de NH3 -> x molar de NH3 (G4-01 define x como molar)."""
    return (w / M_NH3) / ((w / M_NH3) + ((1.0 - w) / M_H2O))


def cronometrar(fn, *a, **kw):
    t0 = time.perf_counter()
    try:
        return fn(*a, **kw), None, time.perf_counter() - t0
    except Exception as exc:                       # se registra el mensaje real
        return None, f"{type(exc).__name__}: {exc}", time.perf_counter() - t0


def main() -> int:
    be = AmmoniaWaterAdapter(x=W_B)
    res: dict = {
        "motor": "src.properties.AmmoniaWaterAdapter (IAPWS G4-01, Tillner-Roth & Friend 1998)",
        "unidades": {"P": "kPa", "T": "K", "h": "kJ/kg", "x": "fraccion MASICA de NH3"},
        "conversion_molar_masica": {
            "molar_a_masica": "w = x*M_NH3 / (x*M_NH3 + (1-x)*M_H2O)",
            "masica_a_molar": "x = (w/M_NH3) / ((w/M_NH3) + ((1-w)/M_H2O))",
            "M_NH3_g_por_mol": M_NH3, "M_H2O_g_por_mol": M_H2O,
        },
        "punto_diseno": {"P_baja_kPa": P_BAJA, "P_alta_kPa": P_ALTA,
                         "w_b_masica_NH3": W_B, "T2_K": T2,
                         "x_b_molar_NH3": masica_a_molar(W_B)},
        "tabla7_re": [
            {"xL_molar_NH3": x, "T_K": T, "p_bub_MPa": p, "xv_molar_NH3": xv}
            for x, T, p, xv in TABLA7],
        "tabla8_re": [
            {"xv_molar_NH3": x, "T_K": T, "p_dew_MPa": p, "xL_molar_NH3": xl}
            for x, T, p, xl in TABLA8],
        "puntos_ciclo": {},
    }

    pc = res["puntos_ciclo"]

    # (a) T de burbuja a P_baja
    v, err, dt = cronometrar(be.bubble_point, P_BAJA, W_B)
    pc["a_Tburbuja_273p55kPa"] = {"T_K": v, "error": err, "segundos": round(dt, 2)}
    print(f"(a) T_burbuja(273.55 kPa, w=0.55) = {v} K  err={err}  [{dt:.1f} s]")

    # (b) T de burbuja y de rocio a P_alta
    v, err, dt = cronometrar(be.bubble_point, P_ALTA, W_B)
    pc["b_Tburbuja_1500kPa"] = {"T_K": v, "error": err, "segundos": round(dt, 2)}
    print(f"(b) T_burbuja(1500 kPa, w=0.55) = {v} K  err={err}  [{dt:.1f} s]")
    v, err, dt = cronometrar(be.dew_point, P_ALTA, W_B)
    pc["b_Trocio_1500kPa"] = {"T_K": v, "error": err, "segundos": round(dt, 2)}
    print(f"(b) T_rocio  (1500 kPa, w=0.55) = {v} K  err={err}  [{dt:.1f} s]")

    # (c) flash T-P a 1500 kPa y 369 K: (xL, xV) masicos + VF por regla de balanza
    v, err, dt = cronometrar(be.equilibrio_liquido_vapor, P_ALTA, T2)
    item = {"error": err, "segundos": round(dt, 2)}
    if v is not None:
        xL, xV = v
        # regla de balanza: w = VF*xV + (1-VF)*xL  ->  VF = (w - xL)/(xV - xL)
        den = xV - xL
        item.update({"xL_masica_NH3": xL, "xV_masica_NH3": xV,
                     "xL_molar_NH3": masica_a_molar(xL), "xV_molar_NH3": masica_a_molar(xV),
                     "vapor_fraction": (W_B - xL) / den if den else None,
                     "nota_VF": "VF por regla de balanza (w - xL)/(xV - xL) a partir de "
                                "equilibrio_liquido_vapor; la interfaz publica no devuelve VF"})
    pc["c_flash_1500kPa_369K"] = item
    print(f"(c) flash(1500 kPa, 369 K): xL={item.get('xL_masica_NH3')} xV={item.get('xV_masica_NH3')} "
          f"VF={item.get('vapor_fraction')} err={err}  [{dt:.1f} s]")

    # (d) Delta h = h(1500 kPa, 369 K) - h(1500 kPa, 300 K)
    h2, e2, d2 = cronometrar(be.h, P_ALTA, T2, W_B)
    h9, e9, d9 = cronometrar(be.h, P_ALTA, T_REFDH, W_B)
    item = {"h_369K_kJ_kg": h2, "h_300K_kJ_kg": h9,
            "error_h_369K": e2, "error_h_300K": e9,
            "segundos": round(d2 + d9, 2)}
    if h2 is not None and h9 is not None:
        item["delta_h_kJ_kg"] = h2 - h9
    pc["d_delta_h_1500kPa_369K_menos_300K"] = item
    print(f"(d) h(1500 kPa,369 K)={h2} kJ/kg  h(1500 kPa,300 K)={h9} kJ/kg  "
          f"delta_h={item.get('delta_h_kJ_kg')} kJ/kg  err={e2 or e9}  [{d2 + d9:.1f} s]")

    # puntos extra utiles para el contraste de saturacion (misma interfaz)
    extra = {}
    for tag, P in (("P_baja_273p55kPa", P_BAJA), ("P_alta_1500kPa", P_ALTA)):
        for nom, fn in (("Tburbuja", be.bubble_point), ("Trocio", be.dew_point)):
            v, err, dt = cronometrar(fn, P, W_B)
            extra[f"{nom}_{tag}"] = {"T_K": v, "error": err}
    res["ciclo_extra"] = extra

    ruta = os.path.join(OUT, "referencia_motor.json")
    with open(ruta, "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=2, ensure_ascii=False)
    print(f"\nescrito: {ruta}")
    return 0


if __name__ == "__main__":
    sys.exit(main())