"""M9 — verificador (final_M9 §Paso 4): recalcula las cifras del reporte y las
compara con `m9_rangos.csv`, `m9_escalera.csv`, `m9_motor_real.csv` y
`m9_husavik.csv`.

No escribe nada: solo imprime `OK`/`FALLA` por cada cifra. Cualquier FALLA
invalida el reporte. Pensado para correr después del paso 4.
"""
from __future__ import annotations

import sys  # noqa: E402
from pathlib import Path

_DIR = Path(__file__).resolve().parent
_RAIZ = _DIR.parents[1]
sys.path[:0] = [str(_RAIZ), str(_DIR)]

import m9_datos as m9  # noqa: E402

TOL = 1e-6
_falla = 0


def chk(nombre, ok, detalle="") -> None:
    global _falla
    if not ok:
        _falla += 1
    print(f'{"OK  " if ok else "FALLA"} {nombre}{" — " + detalle if detalle else ""}',
          flush=True)


def _grupos() -> dict:
    """`{conservados: filas}` de paso 1 y paso 2 juntos."""
    out: dict = {}
    for f in m9.leer(m9.OUT / "m9_paso1.csv"):
        out.setdefault(f["conservados"], []).append(f)
    for f in m9.leer(m9.OUT / "m9_paso2.csv"):
        out.setdefault(f["conservados"], []).append(f)
    return out


def verifica_rangos(grupos) -> None:
    ran = m9.leer(m9.OUT / "m9_rangos.csv")
    for key, rows in grupos.items():
        kal = [f for f in rows if m9.es_kalina(f)]
        conf = [f for f in kal if m9.confiable(f)]
        sub = [r for r in ran if r["conjunto"] == key]
        if not kal:
            chk(f"rangos {key} sin KALINA no aparece", not sub)
            continue
        s = next((r for r in sub if r["ambito"] == "todos los KALINA"
                  and r["variable"] == "dP"), None)
        chk(f"rangos {key}: n KALINA", s is not None and s["n"] == len(kal),
            f'{s["n"] if s else None} vs {len(kal)}')
        s2 = next((r for r in sub if r["ambito"] == "KALINA confiable"
                   and r["variable"] == "dP"), None)
        chk(f"rangos {key}: n KALINA confiable",
            (s2 is None and not conf) or (s2 is not None and s2["n"] == len(conf)),
            f'{s2["n"] if s2 else None} vs {len(conf)}')
        val = [f["dP"] for f in kal if f.get("dP") is not None]
        if val and s:
            chk(f"rangos {key}: mín/máx de dP",
                abs(s["min"] - min(val)) < TOL and abs(s["max"] - max(val)) < TOL)


def verifica_escalera(grupos) -> None:
    for e in m9.leer(m9.OUT / "m9_escalera.csv"):
        rows = grupos.get(e["conservados"], [])
        ds = [f["D"] for f in rows if m9.genu(f) and f.get("D") is not None]
        dm = min(ds) if ds else None
        chk(f'escalera {e["ronda"]}:{e["conservados"]} n_eval',
            e["n_eval"] == len(rows) and len(rows) > 0,
            f'{e["n_eval"]} vs {len(rows)}')
        chk(f'escalera {e["ronda"]}:{e["conservados"]} D_min',
            (dm is None and e["D_min"] is None)
            or (dm is not None and e["D_min"] is not None
                and abs(e["D_min"] - dm) < TOL))


def verifica_motor() -> None:
    for f in m9.leer(m9.OUT / "m9_motor_real.csv"):
        et, er, d = f.get("eta_teqp"), f.get("eta_real"), f.get("d_eta_pp")
        exp = None if et is None or er is None else 100.0 * (er - et)
        chk(f'motor real {f["id"]}: d_eta_pp',
            (exp is None and d is None) or (exp is not None and d is not None
                                            and abs(d - exp) < 1e-6),
            f"{d} vs {exp}")


def verifica_husavik() -> None:
    hus = m9.leer(m9.OUT / "m9_husavik.csv")
    n = 6 if m9.HUMO else 24
    chk("husavik: n.º de corridas", len(hus) == n, f"{len(hus)} vs {n}")
    if hus:
        chk("husavik: dos pisos",
            len({f["piso_tamb"] for f in hus}) == 2)


def main() -> None:
    grupos = _grupos()
    verifica_rangos(grupos)
    verifica_escalera(grupos)
    verifica_motor()
    verifica_husavik()
    print(f"\n{'TODO OK' if _falla == 0 else str(_falla) + ' FALLAS'}", flush=True)
    sys.exit(1 if _falla else 0)


if __name__ == "__main__":
    main()
