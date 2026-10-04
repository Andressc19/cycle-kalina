"""Repite casos de `incertidumbre_eta.py` con el motor real (AmmoniaWaterAdapter) cuando
teqp no cubre el estado perturbado (PropertyRangeError). Misma perturbación, mismo
supuesto (ver docstring de incertidumbre_eta.py). Uso: <punto> <caso>  (p. ej. KALINA-11 xL-)
Agrega la fila a resultados/2026-10-03_incertidumbre_eta/casos_motor_real.csv
"""
import csv, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import incertidumbre_eta as I                                     # noqa: E402
from src.properties.ammonia_water_adapter import AmmoniaWaterAdapter  # noqa: E402


class PerturbadoReal(AmmoniaWaterAdapter):
    """Mismas perturbaciones que `I.Perturbado`, sobre el motor real."""
    def __init__(self, x, dxL=0.0, dyV=0.0, signo_hE=0):
        super().__init__(x=x)
        self.dxL, self.dyV, self.signo_hE = dxL, dyV, signo_hE
    _dh = I.Perturbado._dh

    def h(self, P, T=None, x=None, s=None, quality=None):
        return super().h(P, T=T, x=x, s=s, quality=quality) + self._dh(x)

    def T_from_Ph(self, P, h, x=None):
        return super().T_from_Ph(P, h - self._dh(x), x=x)

    def equilibrio_liquido_vapor(self, P, T):
        wl, wv = super().equilibrio_liquido_vapor(P, T)
        xl = min(max(I.w2m(wl) + self.dxL, 1e-6), 1 - 1e-6)
        yv = min(max(I.w2m(wv) + self.dyV, 1e-6), 1 - 1e-6)
        return I.m2w(xl), I.m2w(yv)


if __name__ == "__main__":
    et, caso = sys.argv[1], sys.argv[2]
    p = I.PUNTOS[et]
    _, dxl, dyv, sg = [c for c in I.CASOS if c[0] == caso][0]
    t0 = time.perf_counter()
    fila = dict(punto=et, caso=caso, motor="real", error="")
    try:
        r = I.resolver_ciclo(PerturbadoReal(p["x_b"], dxl, dyv, sg), **p, **I.COMUN)
        fila.update(eta=r["eta"], Wnet=r["Wnet"], Qi=r["Qi"], m3=r["estados"]["e3"].m)
    except Exception as exc:
        fila["error"] = f"{type(exc).__name__}: {str(exc)[:120]}"
    fila["t_s"] = round(time.perf_counter() - t0, 1)
    f = os.path.join(I.OUT, "casos_motor_real.csv")
    nuevo = not os.path.exists(f)
    with open(f, "a", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["punto", "caso", "motor", "eta", "Wnet", "Qi", "m3", "t_s", "error"])
        if nuevo:
            w.writeheader()
        w.writerow(fila)
    print(fila, flush=True)
