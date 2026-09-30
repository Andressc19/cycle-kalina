"""Fase 2, ronda 6 (2026-09-29-fase2-ronda6-tfuente-libre-xb-alto): T_fuente
LIBRE (380-500 K) x x_b alto (0.70-0.85) x P_alta libre (2800-4500 kPa).
La ronda 5 fijo T_fuente=470 K y hallo un MURO (x_b>=0.70 casi no cierra). Esta
ronda libera T_fuente — la palanca que Karimi & Ahmad (2016) varian. P_baja es
la palanca principal (TASK punto 4) y se barre por COCIENTE DE PRESION rho =
P_baja/P_alta, no absoluto: la frontera O2 (T_sat_L(P_baja,x_b) = T9_amb) la fija
una relacion de presiones, y rho es ademas lo que gobierna eta.
Anti-duplicado: `leer_probadas_r6()` es el de ronda 2 PERO con T_fuente DENTRO
de la clave (9-tuplo); sin eso toda candidata nueva colisionaria con las 945
filas historicas de 470 K.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pandas as pd

_RAIZ = Path(__file__).resolve().parents[3]
if str(_RAIZ) not in sys.path:
    sys.path.insert(0, str(_RAIZ))

T_AMB_DISENO = 303.55
CARPETA = _RAIZ / "resultados" / "barridos_2026-09-19" / "fase2_libre"
CSV = CARPETA / "busqueda_libre_v2.csv"
DIAG = CARPETA / "ronda6_diagnostico.csv"        # companion NUEVO de esta ronda
N_WORKERS, LOTE, S_PT = 4, 10, 42.0     # s/punto: calibracion de esta ronda

# rejillas del TASK
T_FUENTE_GRID = (380., 400., 420., 440., 460., 470., 480., 500.)
X_B_GRID = (0.70, 0.75, 0.80, 0.85)
P_ALTA_GRID = (2800., 3200., 3600., 4000., 4500.)
RHO_CUB = (0.26, 0.36, 0.46)          # escalera gruesa si la campana CUBIERTO
RHO_PAR = (0.32, 0.50, 0.70)          # escalera ancha si la campana es PARCIAL
RATIO_MAX = 0.90                      # mismo tope P_baja < 0.9*P_alta (ronda 4)
ETA_T, ETA_P, EPS_CENTRO = 0.85, 0.75, 0.80   # centros de los rangos del TASK
T_FUENTE_HIST = 470.0                 # ancla historica (las 945 filas previas)

# SIN_PB: clave de columna = todo menos P_baja (AHORA incluye T_fuente).
SIN_PB = ("T_fuente", "P_alta", "x_b", "eta_t", "eta_p", "eps_hrvg", "eps_reg",
          "eps_cond")
# VARS_ENTRADA: clave anti-duplicado completa (9 campos, 3 decimales).
VARS_ENTRADA = ("T_fuente", "P_alta", "P_baja", "x_b", "eta_t", "eta_p",
                "eps_hrvg", "eps_reg", "eps_cond")
ESQUEMA_CSV = ("T_fuente", "T_sumidero", "P_alta", "P_baja", "x_b", "m_b",
               "eta_t", "eta_p", "eps_hrvg", "eps_reg", "eps_cond", "T_sat_L",
               "T9_amb", "O2_margen", "convergio", "clasificacion", "eta",
               "Wnet", "mensaje")
DIAG_COLS = ("T_fuente", "P_alta", "P_baja", "x_b", "eta_t", "eta_p",
             "eps_hrvg", "eps_reg", "eps_cond", "T_bub", "T_dew", "estado_filtro",
             "q2", "q4", "T2", "T_sat_L", "T9_amb", "margen_O1", "margen_O2",
             "margen_S5", "margen_O5", "criterio_ligante", "margen_ligante",
             "al_filo_O1", "convergio", "clasificacion", "eta", "mensaje")


def cargar_r2():
    """ronda2_pbaja por ruta (la carpeta lleva guiones -> no importable)."""
    spec = importlib.util.spec_from_file_location(
        "ronda2_pbaja", Path(__file__).resolve().parent / "ronda2_pbaja.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def tupla(m) -> tuple:
    """9-tuplo de diseno (T_fuente incluida), redondeado a 3 decimales."""
    return tuple(round(float(m[v]), 3) for v in VARS_ENTRADA)


def base_centro() -> dict:
    """Anclas fijas del TASK (punto 7) + centros de etas y efectividades."""
    return dict(cargar_r2().BASE, T_sumidero=300.032917, m_b=1.0, eta_t=ETA_T,
                eta_p=ETA_P, eps_hrvg=EPS_CENTRO, eps_reg=EPS_CENTRO,
                eps_cond=EPS_CENTRO)


def combo(col: dict, rho: float) -> dict:
    """Punto completo a partir de rho = P_baja/P_alta, redondeado a 5 kPa."""
    pa = float(col["P_alta"])
    return dict(col, P_baja=round(min(rho, RATIO_MAX) * pa / 5.0) * 5.0)


def leer_probadas_r6() -> set:
    """9-tuplos ya evaluados en TODOS los CSV de fase2_libre (T_fuente dentro).

    Reconstruye `mapa_2d_pbaja_epscond.csv` con el centro de malla_2d (x_b=0.40,
    resto BASE) igual que ronda 2; tolera que los companions de las rondas 4/5 no
    guarden T_fuente (ancla historica 470 K)."""
    probadas: set = set()
    for f in sorted(CARPETA.glob("*.csv")):
        if f.name == "mapa_2d_pbaja_epscond.csv":
            base = dict(cargar_r2().BASE, x_b=0.40)
            probadas.update(tupla(dict(base, P_baja=r.P_baja, eps_cond=r.eps_cond))
                            for _, r in pd.read_csv(f).iterrows())
            continue
        df = pd.read_csv(f)
        if any(v not in df.columns for v in VARS_ENTRADA if v != "T_fuente"):
            continue
        if "T_fuente" not in df.columns:
            df = df.assign(T_fuente=T_FUENTE_HIST)
        probadas.update(tupla(r) for _, r in df.iterrows())
    assert tupla(dict(cargar_r2().BASE, T_fuente=T_FUENTE_HIST, x_b=0.40,
                      P_baja=400.0, eps_cond=0.95)) in probadas,         "mapa_2d reconstruido no duplica a v2 (400/0.95/0.40)"
    return probadas


def filtrar_campana() -> dict:
    """{celda (T_fuente, x_b, P_alta): T_bub, T_dew, etiqueta} de las 160 celdas.
    Etiquetas (deciden la escalera de rho): FUERA_BUB si T_fuente <= T_bub (el
    HRVG no puede calentar); CUBIERTO si la campana cubre T_fuente; PARCIAL si
    T_fuente >= T_dew pero el HRVG aun da T2 < T_dew porque eps_hrvg < 1."""
    from src.properties.teqp_adapter import TeqpAdapter
    backend, out = TeqpAdapter(x=0.5), {}
    for tf in T_FUENTE_GRID:
        for xb in X_B_GRID:
            for pa in P_ALTA_GRID:
                Tb = float(backend.bubble_point(pa, xb))
                Td = float(backend.dew_point(pa, xb))
                est = ("FUERA_BUB" if tf <= Tb else "CUBIERTO" if tf < Td
                       else "PARCIAL")
                out[(tf, xb, pa)] = dict(T_bub=Tb, T_dew=Td, estado_filtro=est)
    return out


def nivel1(estados: dict) -> tuple:
    """(candidatas, celdas FUERA_BUB) del nivel 1; escalera rho por etiqueta."""
    base, out, fuera = base_centro(), [], []
    for (tf, xb, pa), st in estados.items():
        col = dict(base, T_fuente=tf, P_alta=pa, x_b=xb)
        if st["estado_filtro"] == "FUERA_BUB":
            fuera.append(dict(col, P_baja=float("nan"), **st))
            continue
        rhos = RHO_CUB if st["estado_filtro"] == "CUBIERTO" else RHO_PAR
        out += [dict(combo(col, r), **st) for r in rhos]
    return out, fuera


def leer_diag() -> pd.DataFrame:
    """Companion de la ronda 6 (vacio si aun no existe)."""
    return pd.read_csv(DIAG) if DIAG.exists() else pd.DataFrame(columns=DIAG_COLS)


def por_columna() -> dict:
    """{clave de columna: [(P_baja, margen_O2, eta) convergentes]} del companion."""
    out: dict = {}
    df = leer_diag()
    if df.empty:
        return out
    ok = df[df["convergio"].astype(bool) & df["margen_O2"].notna()]
    for _, r in ok.iterrows():
        k = tuple(round(float(r[v]), 3) for v in SIN_PB)   # todo menos P_baja
        out.setdefault(k, []).append(
            (round(float(r["P_baja"]), 1), float(r["margen_O2"]),
             float(r["eta"]) if pd.notna(r["eta"]) else None))
    return out


def nivel2() -> list:
    """Refina el bracket O2 de cada columna (signo de margen_O2, ancho >= 40 kPa):
    2 puntos interiores sesgados a la P_baja baja (donde eta es mayor), como en
    las rondas 4/5; si ya es KALINA en el piso de escalera, prueba 0.70x."""
    out, base = [], base_centro()
    for k, pts in por_columna().items():
        col = dict(base, T_fuente=k[0], P_alta=k[1], x_b=k[2], eta_t=k[3],
                   eta_p=k[4], eps_hrvg=k[5], eps_reg=k[6], eps_cond=k[7])
        s = sorted(pts)
        br = [(p1, p2) for (p1, m1, _), (p2, m2, _) in zip(s, s[1:])
              if m1 * m2 < 0 and p2 - p1 >= 40.0]
        if br:
            p1, p2 = max(br, key=lambda b: b[1] - b[0])
            out += [dict(col, P_baja=round(p1 + f * (p2 - p1))) for f in (0.25, 0.65)]
        elif [q for q in pts if q[1] > 0.0]:      # KALINA en el piso -> mas abajo
            out.append(dict(col, P_baja=max(50.0, round(0.70 * min(pts)[0]))))
    return out


def nivel3(por_xb: int = 3) -> list:
    """Palanecas autorizadas sobre la mejor frontera O2 de cada (T_fuente, x_b).
    eps_cond es la palanca DIRECTA de O2 (lo dice su propio mensaje): sube O2 a
    P_baja baja -> mayor relacion de presiones -> mas eta. Extremos 0.85/0.75 de
    eps_cond, 0.90/0.80 de eta_t y 0.85/0.75 de (eps_hrvg, eps_reg) sobre los
    `por_xb` mejores KALINA con |margen_O2| <= 3 K de la celda."""
    df = leer_diag()
    if df.empty:
        return []
    ok = df[(df["clasificacion"] == "KALINA") & df["margen_O2"].between(-3.0, 3.0)
            & df["eta"].notna()]
    out, base = [], base_centro()
    for (tf, xb), g in ok.groupby(["T_fuente", "x_b"]):
        for _, r in g.nlargest(por_xb, "eta").iterrows():
            col = dict(base, T_fuente=float(tf), P_alta=float(r["P_alta"]),
                       x_b=float(xb), eta_t=float(r["eta_t"]),
                       eta_p=float(r["eta_p"]), P_baja=float(r["P_baja"]))
            out += [dict(col, eps_cond=0.85), dict(col, eps_cond=0.75),
                    dict(col, eta_t=0.90), dict(col, eta_t=0.80),
                    dict(col, eps_hrvg=0.85, eps_reg=0.85),
                    dict(col, eps_hrvg=0.75, eps_reg=0.75)]
    return out
