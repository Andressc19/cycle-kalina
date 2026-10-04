"""Sonda 2026-10-03: por que la BOMBA devuelve T10 < T9 (Wp negativo) en el lazo.

Fija S9 como lo hace el lazo de efectividad y resuelve UNA vez, imprimiendo T, P, m,
w, entalpia de fase 0, VF y el numero de fases de cada corriente, mas el trabajo que
reporta DWSIM. Correccion:  python -u <este archivo>
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "scripts", "dwsim"))
import _kcs11_dwsim_base as B          # noqa: E402

P_A, P_B, T_F, T_S = B.PUNTOS[0][2], B.PUNTOS[0][4], B.PUNTOS[0][3], B.PUNTOS[0][5]
X_B = B.PUNTOS[0][1]
d = B.diagrama(P_A, P_B, X_B, 1.0, 0.80, 0.80)
d["eq"]["reg"].MITA = 5.5
d["eq"]["hrvg"].DeltaQ = 476.0
d["eq"]["cond"].DeltaQ = 392.0
B.fijar(d, "S5", 369.0, P_A, 0.3873, 0.71918)

print("%-9s %6s %5s %5s %5s %7s %7s %5s %s" % ("corr", "nF", "T", "P", "vf", "h0", "h_PT", "w", ""))
for T9 in (287.0, 285.7):
    B.fijar(d, "S9", T9, P_B, X_B, 1.0)
    errs = [str(e).splitlines()[0][:60] for e in B.resolver(d)]
    print("\n=== S9 fijado a %.2f K | errores: %s ===" % (T9, errs or "ninguno"))
    for n in ("S9", "S10", "S1", "S5", "S6", "S7", "S8", "S9c", "S2", "S3"):
        st = d["S"][n].GetAsObject()
        fases = len(st.Phases)
        pr = B.props(d, n)
        vfs = [round(float(st.Phases[i].Properties.molarfraction), 4)
               if st.Phases[i].Properties.molarfraction is not None else None
               for i in range(fases)]
        h_pt = B.h_PT(d, pr["P"], pr["T"], pr["w"])
        print("%-9s %6d %5.1f %5.1f %5s %7.2f %7.2f %5.4f %s"
              % (n, fases, pr["T"], pr["P"], str(vfs), pr["h"], h_pt, pr["w"],
                 "h0-h_PT=%+.3f" % (pr["h"] - h_pt)))
    print("  Wp(DWSIM)=%.4f  Wp(corrientes S10-S9)=%.4f  Wt=%.4f  Q_hrvg=%.4f  Q_cond=%.4f"
          % (B.energia(d, "W_bomba"), B.props(d, "S10")["h"] - B.props(d, "S9")["h"],
             B.energia(d, "W_turb"), B.energia(d, "Q_hrvg"), B.energia(d, "Q_cond")))