"""Parte C (copia MEJORADA de `benchmark_extrapolacion.py`) — extrapolación de los
costes MEDIDOS a cada barrido histórico, usando la configuración de MB ELEGIDA en A4
en vez de la que salía del criterio antiguo.

No modifica `benchmark_extrapolacion.py` (evidencia). Cambios frente a aquel:

  * `MB(...)` usa la configuración elegida en A4 (no `mejor_cfg`, que aplicaba el
    criterio viejo sobre topes que no son V2) y sus costes MEDIDOS en A2
    (`benchmark_filas_topes.csv`), no los de la Parte A con tope 6;
  * `t_sana_*` se mide SOLO sobre las filas que ese modo resuelve de verdad (con el
    antiguo se promediaban las 30 sanas, una de las cuales M0 no resuelve, y por eso
    `MB` y `M0` share el mismo coste de fila sana: es correcto, MB corre M0 primero,
    pero ahora se explicita);
  * se añade `t_pared_extrapolado_min` por modo y una columna que separa lo MEDIDO de
    lo EXTRAPOLADO fila a fila, más el tiempo real conocido de cada barrido.

Modelo (explícito en el CSV): para un barrido con `s` filas que su propio CSV reporta
convergentes y `f` filas `NO_CONVERGIO`,
    t_M0  = s·t_sana_M0 + f·t_falla_M0
    t_MB  = s·t_sana_M0 + f·t_falla_MB     (MB corre M0 primero: en las sanas es M0)
    t_MA  = s·t_sana_MA + f·t_falla_MA
con `t_sana` el coste medio de una fila que ese modo resuelve y `t_falla` el de una
fila que no resuelve. Los tiempos de pared son CPU/6 workers.

Uso:  python scripts/benchmark_extrapolacion_cierre.py <config_elegida_en_A4>
"""
import sys
from pathlib import Path

_RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_RAIZ))
sys.path.insert(0, str(_RAIZ / "scripts"))

import pandas as pd                                                       # noqa: E402
from benchmark_cierre_modos import CSV_A, CSV_ABL, CSV_TOPES, OUT         # noqa: E402

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
             "barrido_xb_industria": "REPORTE_XB_INDUSTRIA.md: 'corrida total ~ 65 min en 4 "
                                     "tandas' (0.1-100 s/punto; el reporte da el total, no "
                                     "el desglose). Ademas: costo_soluciones 30.98 s/punto "
                                     "con teqp"}
SIN_DATO = "sin dato registrado"


def costes(elegido):
    """Costes por tipo de fila, todos MEDIDOS. `sana_*` se mide solo sobre las filas
    que el modo resuelve; `falla_*` sobre las que no."""
    a, abl = pd.read_csv(CSV_A), pd.read_csv(CSV_ABL)
    sana = a[a.etapa == "A2"]                                    # 30 filas sanas
    fall = a[(a.etapa == "A1") & (a.config == "M0")]            # las 40 que M0 no resuelve
    ab_sana, ab_fall = abl[abl.V0 == "convergio"], abl[abl.V0 != "convergio"]
    m0_sana = sana[sana.config == "M0"]
    mb = pd.read_csv(CSV_TOPES).query("config == @elegido")     # las 40 con MB
    sana_M0 = float(m0_sana[m0_sana.convergio].t_s.mean())
    c = dict(
        elegido=elegido,
        sana_M0=sana_M0,
        sana_MB=sana_M0,          # MB corre M0 primero: en una fila sana es M0 exacto
        sana_MA=float(ab_sana.V2_t_s.mean()),
        falla_M0=float(fall.t_s.mean()),
        falla_MB=float(mb[~mb.convergio].t_s.mean()),
        falla_MA=float(ab_fall.V2_t_s.mean()),
        n_sana=int(len(m0_sana)), n_sana_M0=int(m0_sana.convergio.sum()),
        n_fall=int(len(fall)), n_fall_MB=int((~mb.convergio).sum()))
    return c


def main() -> None:
    elegido = sys.argv[1]
    OUT.mkdir(parents=True, exist_ok=True)
    c = costes(elegido)
    print(f"Configuración de MB: {elegido}\nCostes MEDIDOS por tipo de fila:")
    for k in ("sana_M0", "sana_MB", "sana_MA", "falla_M0", "falla_MB", "falla_MA"):
        print(f"  {k:9s} = {c[k]:8.2f} s")
    print(f"  (filas sanas medidas: {c['n_sana']}, de las que M0 resuelve "
          f"{c['n_sana_M0']} — MB corre M0 primero, asi que su coste en una fila sana "
          f"es el de M0; filas que M0 no resuelve: {c['n_fall']}, de las que {elegido} "
          f"sigue sin resolver {c['n_fall_MB']})")
    filas = []
    for nombre, rel in BARRIDOS:
        d = pd.read_csv(_RAIZ / "resultados" / rel)
        n, k = int(d.shape[0]), int((d.clasificacion == "NO_CONVERGIO").sum())
        s, f = n - k, k
        est = {"M0": (s, c["sana_M0"], f, c["falla_M0"]),
               f"MB({elegido})": (s, c["sana_M0"], f, c["falla_MB"]),
               "MA (=V2)": (s, c["sana_MA"], f, c["falla_MA"])}
        for modo, (ns, ts, nf, tf) in est.items():
            filas.append(dict(
                barrido=nombre, filas_totales=n, filas_NO_CONVERGIO=k,
                filas_convergentes=s, modo=modo,
                filas_sanas_aplicadas=ns, filas_fallidas_aplicadas=nf,
                t_sana_aplicado_s=round(ts, 3), t_falla_aplicado_s=round(tf, 3),
                origen_coste_sana=("MEDIDO (benchmark_filas.csv, etapa A2: las 30 sanas "
                                   "que M0 resuelve)" if modo != "MA (=V2)" else
                                   "MEDIDO (V2 de ablacion_filas.csv; MA no recalculado "
                                   "por indicacion del director)"),
                origen_coste_falla=("MEDIDO (benchmark_filas.csv etapa A1 + "
                                    "benchmark_filas_topes.csv; solo las filas que "
                                    f"{elegido} NO resuelve)" if modo != "MA (=V2)" else
                                    "MEDIDO (V2 de ablacion_filas.csv sobre las 40 que "
                                    "V0 no resuelve)"),
                filas_y_no_convergio="MEDIDO (propio CSV del barrido)",
                t_cpu_extrapolado_s=round(ns * ts + nf * tf, 1),
                t_pared_extrapolado_s=round((ns * ts + nf * tf) / N_WORKERS, 1),
                t_pared_extrapolado_min=round((ns * ts + nf * tf) / N_WORKERS / 60.0, 2),
                tiempo_real_conocido_s=REAL_S.get(nombre),
                tiempo_real_nota=REAL_NOTA.get(nombre, SIN_DATO),
                extrapolacion=("SI — costes MEDIDOS de la muestra aplicados a este "
                               "barrido; el barrido NO se ejecuto con estos modos. Ojo: "
                               "las filas que el propio barrido marca NO_CONVERGIO no "
                               "son necesariamente las que estos modos fallarian")))
        print(f"  {nombre:26s} {n:5d} filas, {k:5d} NO_CONVERGIO (propio CSV)")
    df = pd.DataFrame(filas)
    assert (df.groupby("barrido").filas_totales.nunique() == 1).all()
    g = df.groupby("barrido")
    assert (g.filas_totales.first()
            == g.filas_convergentes.first() + g.filas_NO_CONVERGIO.first()).all(), "no suma"
    assert (g.filas_sanas_aplicadas.first() == g.filas_convergentes.first()).all()
    assert (g.filas_fallidas_aplicadas.first() == g.filas_NO_CONVERGIO.first()).all()
    assert (g.modo.nunique() == 3).all()
    assert (g.filas_totales.first()
            == (g.filas_sanas_aplicadas.first() + g.filas_fallidas_aplicadas.first())
            ).all(), "sanas+fallidas != totales"
    df.to_csv(CSV_OUT, index=False)
    print(f"\nControl de sumas OK: {df.barrido.nunique()} barridos x "
          f"{df.modo.nunique()} modos = {len(df)} filas; en cada fila "
          f"filas_convergentes + filas_NO_CONVERGIO = filas_totales")
    print("\nTiempo de PARED extrapolado (min), 6 workers:")
    print(df.pivot(index="barrido", columns="modo",
                   values="t_pared_extrapolado_min").round(1).to_string())
    print(f"\n{len(df)} filas -> {CSV_OUT}")


if __name__ == "__main__":
    main()
