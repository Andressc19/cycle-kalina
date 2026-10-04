"""Diagnostico: flash P-T de liquido comprimido (5000 kPa, 314.49 K, xm NH3=0.6627) con PR."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "scripts", "dwsim"))
import _kcs11_dwsim_base as B
casos = [(5000.0, 314.49, 0.65), (5000.0, 303.2, 0.65), (5000.0, 340.0, 0.65), (4000.0, 314.0, 0.80), (1101.5, 310.0, 0.80)]
variantes = {"base": {}, "PTdamp0.5": {"PTFlash_DampingFactor": "0.5"}, "IO": {"UseIOFlash": "True"},
             "estab": {"CheckIncipientLiquidForStability": "True"}, "VLE": {"ForceEquilibriumCalculationType": "VLE"},
             "tolPT1e-6": {"PTFlash_External_Loop_Tolerance": "1e-6", "PTFlash_Internal_Loop_Tolerance": "1e-6"}}
for nom, extra in variantes.items():
    aj = dict(B.AJUSTES, **extra); B.AJUSTES.clear(); B.AJUSTES.update(aj)
    d = B.diagrama(5000.0, 700.0, 0.65, 1.0, 0.8, 0.8)
    out = []
    for P, T, w in casos:
        try:
            out.append("%.0f/%.1f/%.2f h=%.2f" % (P, T, w, B.h_PT(d, P, T, w)))
        except Exception as e:
            out.append("%.0f/%.1f/%.2f FALLA" % (P, T, w))
    print("%-10s" % nom, " | ".join(out), flush=True)
    for k in extra: B.AJUSTES.pop(k, None)
