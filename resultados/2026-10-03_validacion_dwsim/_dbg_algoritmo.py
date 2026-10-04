"""Diagnostico: algoritmos de flash de DWSIM en los estados de liquido comprimido que fallan."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "scripts", "dwsim"))
import _kcs11_dwsim_base as B
B.runtime()
import clr
from DWSIM.Thermodynamics.PropertyPackages.Auxiliary import FlashAlgorithms as FA
algs = [n for n in dir(FA) if not n.startswith("_")]
print("disponibles:", algs)
casos = [(5000.0, 314.5, 0.65), (5000.0, 301.0, 0.80), (4000.0, 300.5, 0.80), (5000.0, 315.0, 0.70), (1500.0, 369.0, 0.55)]
for nom in ("NestedLoops", "BostonBrittInsideOut", "BostonFournierInsideOut3P", "GibbsMinimization3P", "NestedLoops3PV3", "UniversalFlash", "SimpleLLE"):
    if not hasattr(FA, nom):
        continue
    d = B.diagrama(5000.0, 700.0, 0.65, 1.0, 0.8, 0.8)
    try:
        d["pp"].FlashAlgorithm = getattr(FA, nom)()
    except Exception as e:
        print("%-28s no asignable: %s" % (nom, str(e)[:80])); continue
    out = []
    for P, T, w in casos:
        try:
            out.append("%.0f/%.1f/%.2f h=%.2f" % (P, T, w, B.h_PT(d, P, T, w)))
        except Exception:
            out.append("%.0f/%.1f/%.2f FALLA" % (P, T, w))
    print("%-28s" % nom, " | ".join(out), flush=True)
