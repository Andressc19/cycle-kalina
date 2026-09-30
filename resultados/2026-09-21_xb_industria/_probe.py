import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.properties.adapter import PropertyRangeError
from src.properties.teqp_adapter import TeqpAdapter
from src.cycle_solver import resolver_ciclo


def probe(xb, P_alta, P_baja=400.0):
    b = TeqpAdapter(x=xb)
    t0 = time.time()
    try:
        r = resolver_ciclo(
            b, P_alta=P_alta, P_baja=P_baja, T_fuente=470.0,
            T_sumidero=300.032917, x_b=xb, m_b=1.0, eta_t=0.85, eta_p=0.75,
            eps_hrvg=0.85, eps_reg=0.75, eps_cond=0.80)
        e2 = r["estados"]["e2"]
        _, q2 = b.fase_de(P_alta, e2.T, xb)
        return (f"CONV T2={e2.T:.2f} q2={q2:.4f} eta={r['eta']:.5f} "
                f"({time.time()-t0:.1f}s)")
    except PropertyRangeError as ex:
        return f"DOM {str(ex)[:70].replace(chr(10), ' ')} ({time.time()-t0:.1f}s)"
    except Exception as ex:
        return f"{type(ex).__name__}: {str(ex)[:70]} ({time.time()-t0:.1f}s)"


if __name__ == "__main__":
    xb = float(sys.argv[1])
    for P in range(6000, 10500, 500):
        print(f"P={P}:", probe(xb, P))
    print("--- beyond 10000 ---")
    for P in (11000, 12000, 14000, 16000):
        print(f"P={P}:", probe(xb, P))