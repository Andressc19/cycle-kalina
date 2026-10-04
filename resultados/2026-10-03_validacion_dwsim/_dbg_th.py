"""Sonda 2026-10-03: verifica la cadena de efectividad con la inversion `T_de_h`.

Si la cadena es correcta, aplicar las ecuaciones del proyecto al estado pinch de la
plantilla (`kcs11_elsayed_dwsim.py`) debe devolver EXACTAMENTE los estados de la
plantilla: T6 = 303.83 K y T9 = 287.00 K. Correccion:  python -u <este archivo>
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "scripts", "dwsim"))
import _kcs11_dwsim_base as B          # noqa: E402

P_A, P_B, T_F, T_S = B.PUNTOS[0][2], B.PUNTOS[0][4], B.PUNTOS[0][3], B.PUNTOS[0][5]
X_B, EPS = B.PUNTOS[0][1], B.PUNTOS[0][6]
E, S, M = B.PINCH_ELSAYED, B.PINCH_ELSAYED, 1.0

d = B.diagrama(P_A, P_B, X_B, M, 0.80, 0.80)
print("P_alta=%.1f kPa  P_baja=%.4f kPa  T_fuente=%.1f K  T_sumidero=%.1f K"
      % (P_A, P_B, T_F, T_S))

# --- regenerador: h6 = h5 - eps_reg*(h5 - h(P_alta,T10,x5)) -> T6 esperado 303.83 K
h5 = B.h_PT(d, P_A, E["T5"], E["x5"])
h6min = B.h_PT(d, P_A, E["T10"], E["x5"])
h6t = h5 - EPS[1] * (h5 - h6min)
T6 = B.T_de_h(d, P_A, h6t, E["x5"], E["T10"], E["T5"])
print("regenerador: h5=%.4f  h6min=%.4f  h6,objetivo=%.4f -> T6=%.4f K "
      "(plantilla %.2f, d=%+.2e K)"
      % (h5, h6min, h6t, T6, E["T6"], T6 - E["T6"]))

# --- condensador: h9 = h8 - eps_cond*(h8 - h(P_baja,T_sumidero,x8)) -> T9 esperado 287.0 K
h8 = B.h_PT(d, P_B, E["T8"], X_B)
h9min = B.h_PT(d, P_B, T_S, X_B)
h9t = h8 - EPS[2] * (h8 - h9min)
T9 = B.T_de_h(d, P_B, h9t, X_B, T_S, E["T8"])
print("condensador: h8=%.4f  h9min=%.4f  h9,objetivo=%.4f -> T9=%.4f K "
      "(plantilla %.2f, d=%+.2e K)"
      % (h8, h9min, h9t, T9, E["T9"], T9 - E["T9"]))

# --- HRVG: Qi = m_b*eps_hrvg*(h(P_alta,T_fuente,x_b) - h1) con h1 del estado pinch
h1 = B.h_PT(d, P_A, E["T1"], X_B)
h2max = B.h_PT(d, P_A, T_F, X_B)
print("HRVG: h1=%.4f  h2max=%.4f -> Qi=%.4f kW (plantilla 452.462, d=%+.4f kW)"
      % (h1, h2max, M * EPS[0] * (h2max - h1), M * EPS[0] * (h2max - h1) - 452.462))
print("Qi/Qout con m_b*eps: Qi=%.4f  Qout=%.4f kW (plantilla 397.240)"
      % (M * EPS[0] * (h2max - h1), M * EPS[2] * (h8 - h9min)))