"""Diagnostico: franja de T donde falla el flash P-T de PR (liquido comprimido, w=0.65 y 0.80)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "scripts", "dwsim"))
import _kcs11_dwsim_base as B
d = B.diagrama(5000.0, 700.0, 0.65, 1.0, 0.8, 0.8)
for P, w in ((5000.0, 0.65), (5000.0, 0.80), (4000.0, 0.80), (3000.0, 0.60), (5000.0, 0.70)):
    fallas = []
    for i in range(0, 121):
        T = 300.0 + 0.5 * i
        try:
            B.h_PT(d, P, T, w)
        except Exception:
            fallas.append(T)
    print("P=%.0f w=%.2f fallas=%d  %s" % (P, w, len(fallas), (str(fallas[:3]) + "..." + str(fallas[-3:])) if fallas else ""), flush=True)
