"""Parte C — extrapolación de los costes medidos a cada barrido histórico.

Toma los TIEMPOS MEDIDOS en la Parte A (`benchmark_filas.csv`) y los de MA, que
por indicación del director NO se recalculan sino que se toman de la ablación
(`ablacion_filas.csv`, variante V2 = MA). Los conteos de filas y de
`NO_CONVERGIO` salen de los PROPIOS CSV de cada barrido.

Es una EXTRAPOLACIÓN: los barridos no se ejecutaron con estos modos; se les
asignan los costes medios por tipo de fila medidos en la muestra de 56 filas.
Cada fila del CSV lleva `origen_del_coste` para distinguir qué es medida y qué
es extrapolado.

Uso:  python scripts/benchmark_extrapolacion.py
"""
import sys
from pathlib import Path

_RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_RAIZ))
sys.path.insert(0, str(_RAIZ / "scripts"))

import pandas as pd                                                       # noqa: E402
from benchmark_reintento_tolerante import CSV_A, CSV_ABL, OUT, mejor_cfg  # noqa: E402

CSV_OUT = OUT / "extrapolacion_barridos.csv"
N_WORKERS = 6
BARRIDOS = (("busqueda_libre_v2", "barridos_2026-09-19/fase2_libre/busqueda_libre_v2.csv"),
            ("ronda5_diagnostico", "barridos_2026-09-19/fase2_libre/ronda5_diagnostico.csv"),
            ("ronda6_diagnostico", "barridos_2026-09-19/fase2_libre/ronda6_diagnostico.csv"),
            ("barrido_xb_industria", "2026-09-21_xb_industria/barrido_xb_industria.csv"),
            ("barrido_literatura_kcs11", "2026-09-22_literatura_kcs11/barrido_literatura_kcs11.csv"),
            ("barrido_margen2k", "2026-09-24_margen2k/barrido_margen2k.csv"),
            ("barrido_pinch6_realista", "2026-09-23_pinch6_realista/barrido_pinch6_realista.csv"))
# Tiempo real conocido (MEDIDO en su corrida original), del reporte o del run.log.
REAL_S = {"barrido_margen2k": 8369.0, "barrido_pinch6_realista": 1797.0,
          "barrido_xb_industria": 65 * 60.0}
REAL_NOTA = {"barrido_margen2k": "run.log: 'Malla completa en 8369s'",
             "barrido_pinch6_realista": "run.log: 'Malla completa en 1797s'",
             "barrido_xb_industria": "REPORTE_XB_INDUSTRIA.md: 'corrida total ~ 65 min en 4 tandas' "
                                     "(0.1-100 s/punto; el reporte da el total, no el desglose)"}


def costes():
    """Costes por tipo de fila. MEDIDOS en benchmark_filas.csv salvo MA (V2 de la
    ablación, por indicación del director de no recalcularlo)."""
    a, abl = pd.read_csv(CSV_A), pd.read_csv(CSV_ABL)
    mejor, _, _ = mejor_cfg(a)
    sana = a[(a.etapa == "A2") & (a.config == "M0")]
    fall = a[(a.etapa == "A1") & (a.config == "M0")]
    ab_fall, ab_sana = abl[abl.V0 != "convergio"], abl[abl.V0 == "convergio"]
    return dict(
        mejor=mejor,
        sana_M0=float(sana.t_s.mean()), sana_MA=float(ab_sana.V2_t_s.mean()),
        falla_M0=float(fall.t_s.mean()),
        falla_MB=float(a[(a.etapa == "A1") & (a.config == mejor)].t_s.mean()),
        falla_MA=float(ab_fall.V2_t_s.mean()),
        n_sana=len(sana), n_fall=len(fall))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    c = costes()
    print(f"Mejor MB: {c['mejor']}")
    for k in ("sana_M0", "sana_MA", "falla_M0", "falla_MB", "falla_MA"):
        print(f"  coste medio fila {k:9s} = {c[k]:8.2f} s")
    filas = []
    for nombre, rel in BARRIDOS:
        d = pd.read_csv(_RAIZ / "resultados" / rel)
        n, k = int(d.shape[0]), int((d.clasificacion == "NO_CONVERGIO").sum())
        s, f = n - k, k
        est = {"M0": s * c["sana_M0"] + f * c["falla_M0"],
               "MA": s * c["sana_MA"] + f * c["falla_MA"],
               f"MB({c['mejor']})": s * c["sana_M0"] + f * c["falla_MB"]}
        for modo, cpu in est.items():
            filas.append(dict(
                barrido=nombre, filas_totales=n, filas_NO_CONVERGIO=k, filas_convergentes=s,
                modo=modo,
                t_sana_aplicado=round(c["sana_MA"] if modo == "MA" else c["sana_M0"], 3),
                t_falla_aplicado=round(c[{"M0": "falla_M0", "MA": "falla_MA"}.get(
                    modo, "falla_MB")], 3),
                origen_del_coste="MEDIDO (benchmark_filas.csv)" if modo != "MA"
                else "MEDIDO (V2 de ablacion_filas.csv; MA no recalculado)",
                filas_y_no_convergio="MEDIDO (propio CSV del barrido)",
                t_cpu_extrapolado_s=round(cpu, 1),
                t_pared_extrapolado_s=round(cpu / N_WORKERS, 1),
                t_pared_extrapolado_min=round(cpu / N_WORKERS / 60.0, 2),
                tiempo_real_conocido_s=REAL_S.get(nombre),
                tiempo_real_nota=REAL_NOTA.get(nombre, "sin dato registrado"),
                extrapolacion=("SI — costes de la muestra de 56 filas aplicados a este barrido; "
                               "el barrido NO se ejecutó con estos modos")))
    df = pd.DataFrame(filas)
    df.to_csv(CSV_OUT, index=False)
    print(f"\n{len(df)} filas -> {CSV_OUT}")
    print(df.pivot(index="barrido", columns="modo",
                   values="t_pared_extrapolado_min").round(1).to_string())


if __name__ == "__main__":
    main()