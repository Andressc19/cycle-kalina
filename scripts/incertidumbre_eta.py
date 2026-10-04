"""Banda de incertidumbre de η por la incertidumbre del modelo de propiedades (2026-10-03).

Propaga a η las incertidumbres publicadas del modelo Tillner-Roth & Friend (IAPWS G4-01 §7,
ver CONTEXT.md): composiciones de equilibrio L-V ±0.01 (fracción molar) y entalpía de
exceso ±200 J/mol. Método aprobado por el usuario: perturbar una cosa a la vez (+ y −),
resolver el ciclo con el solver del proyecto y combinar las semibandas en RSS.

Supuestos (estimación de primer orden, documentados en el reporte):
- Forma de la perturbación de entalpía: δh = ±200·4·xm·(1−xm) J/mol (cero en los puros,
  máxima a xm=0.5), convertida a kJ/kg con la masa molar de la mezcla. G4-01 da solo la cota.
- Se perturba h (y su inversa T_from_Ph) pero no s.
- Backend: `TeqpVerificado` (η equivalente al motor real, < 0.002 pp en 6 puntos).
`src/` no se modifica: la perturbación vive en una subclase de este script.
Salida: resultados/2026-10-03_incertidumbre_eta/{casos.csv, banda.csv}
"""
import csv
import math
import os
import sys
import time

REPO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, REPO)
from src.cycle_solver import resolver_ciclo                      # noqa: E402
from src.properties.teqp_verificado import TeqpVerificado        # noqa: E402
from src.properties._teqp_engine import w2m, m2w                 # noqa: E402

OUT = os.path.join(REPO, "resultados", "2026-10-03_incertidumbre_eta")
M_A, M_W = 17.03052, 18.015268
DX_VLE, DH_E = 0.01, 200.0          # fracción molar; J/mol (IAPWS G4-01 §7)
PUNTOS = {
    "ELSAYED": dict(P_alta=1500.0, P_baja=273.5454214157179, T_fuente=373.0, x_b=0.55,
                    eps_hrvg=0.8882023116022899, eps_reg=0.9380325550010874, eps_cond=0.9625029043677631),
    "KALINA-01": dict(P_alta=3000.0, P_baja=523.749936, T_fuente=394.0, x_b=0.60,
                      eps_hrvg=0.85, eps_reg=0.80, eps_cond=0.85),
    "KALINA-11": dict(P_alta=5000.0, P_baja=704.644595, T_fuente=423.0, x_b=0.65,
                      eps_hrvg=0.85, eps_reg=0.80, eps_cond=0.85),
}
COMUN = dict(T_sumidero=283.0, m_b=1.0, eta_t=0.80, eta_p=0.80)
# (nombre, dxL, dyV, signo_hE): una perturbación a la vez
CASOS = [("base", 0, 0, 0), ("xL+", DX_VLE, 0, 0), ("xL-", -DX_VLE, 0, 0),
         ("yV+", 0, DX_VLE, 0), ("yV-", 0, -DX_VLE, 0), ("hE+", 0, 0, 1), ("hE-", 0, 0, -1)]


class Perturbado(TeqpVerificado):
    """TeqpVerificado con el equilibrio L-V y/o la entalpía de exceso desplazados."""

    def __init__(self, x, dxL=0.0, dyV=0.0, signo_hE=0):
        super().__init__(x=x)
        self.dxL, self.dyV, self.signo_hE = dxL, dyV, signo_hE

    def _dh(self, x):
        """δh [kJ/kg] = signo·200·4·xm(1−xm) J/mol / M_mezcla [g/mol]."""
        if not self.signo_hE:
            return 0.0
        xm = w2m(self._x if x is None else x)
        return self.signo_hE * DH_E * 4.0 * xm * (1.0 - xm) / (xm * M_A + (1.0 - xm) * M_W)

    def h(self, P, T=None, x=None, s=None, quality=None):
        return super().h(P, T=T, x=x, s=s, quality=quality) + self._dh(x)

    def T_from_Ph(self, P, h, x=None):
        return super().T_from_Ph(P, h - self._dh(x), x=x)

    def equilibrio_liquido_vapor(self, P, T):
        wl, wv = super().equilibrio_liquido_vapor(P, T)
        xl = min(max(w2m(wl) + self.dxL, 1e-6), 1 - 1e-6)
        yv = min(max(w2m(wv) + self.dyV, 1e-6), 1 - 1e-6)
        return m2w(xl), m2w(yv)


def main():
    os.makedirs(OUT, exist_ok=True)
    filas = []
    f = open(os.path.join(OUT, "casos.csv"), "w", newline="", encoding="utf-8")
    w = csv.DictWriter(f, fieldnames=["punto", "caso", "eta", "Wnet", "Qi", "m3", "x3", "x5", "t_s", "error"])
    w.writeheader()
    for et, p in PUNTOS.items():
        for nom, dxl, dyv, sg in CASOS:
            be = Perturbado(p["x_b"], dxl, dyv, sg)
            t0 = time.perf_counter()
            fila = dict(punto=et, caso=nom, error="")
            try:
                r = resolver_ciclo(be, **p, **COMUN)
                e = r["estados"]
                fila.update(eta=r["eta"], Wnet=r["Wnet"], Qi=r["Qi"], m3=e["e3"].m, x3=e["e3"].x, x5=e["e5"].x)
            except Exception as exc:                       # se registra, no se inventa
                fila["error"] = f"{type(exc).__name__}: {str(exc)[:120]}"
            fila["t_s"] = round(time.perf_counter() - t0, 1)
            w.writerow(fila); f.flush(); filas.append(fila)
            print(et, nom, "eta=%s" % fila.get("eta"), fila["error"], fila["t_s"], "s", flush=True)
    f.close()
    banda = []
    for et in PUNTOS:
        c = {r["caso"]: r for r in filas if r["punto"] == et and not r["error"]}
        if "base" not in c:
            continue
        semi = {}
        for g in ("xL", "yV", "hE"):
            vals = [c[k]["eta"] for k in (g + "+", g + "-") if k in c]
            semi[g] = max(abs(v - c["base"]["eta"]) for v in vals) if vals else float("nan")
        rss = math.sqrt(sum(v * v for v in semi.values()))
        banda.append(dict(punto=et, eta_base=100 * c["base"]["eta"],
                          semi_xL_pp=100 * semi["xL"], semi_yV_pp=100 * semi["yV"], semi_hE_pp=100 * semi["hE"],
                          banda_RSS_pp=100 * rss))
        print(banda[-1], flush=True)
    with open(os.path.join(OUT, "banda.csv"), "w", newline="", encoding="utf-8") as fb:
        wb = csv.DictWriter(fb, fieldnames=list(banda[0])); wb.writeheader(); wb.writerows(banda)


if __name__ == "__main__":
    main()
