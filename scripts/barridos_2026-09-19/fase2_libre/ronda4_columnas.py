"""Fase 2, ronda 4 (tarea 2026-09-28-fase2-ronda4-campana-3h) — grilla de la
campana extendida. Modulo hermano de `ronda4_campana.py` (lo usa el runner y
`ronda4_informe.py`); centraliza el esquema de exploracion para que las dos
piezas no puedan desincronizarse.

Por que esta grilla y no la de las rondas 1-3: el TASK_CONTEXT de esta ronda
exige reglas de realismo MAS ESTRICTAS. Lo que se mueve son las
efectividades, que quedan ESTRICTAMENTE en [0.75, 0.85] (el techo de eps_cond
baja de 0.95 a 0.85), y x_b, que NO se baja: se queda en [0.40, 0.50] (las
rondas 2-3 bajaban x_b a 0.35 para relajar el criterio O2; aqui esa palanca
esta vedada). Con eps_cond topado en 0.85 el criterio O2 se cierra subiendo
P_baja, y eso es justo lo que hay que medir: hasta donde hay que llegar con
P_baja para compensar el techo mas bajo de efectividades. Por eso P_baja se
explora en un rango AMPLIO (650 kPa hasta 0.90*P_alta), muy por encima de los
~800 kPa como maximo que cubrieron las rondas anteriores.

Ancla FIJA de toda la ronda: T_fuente=470.0 K, T_sumidero=300.032917 K,
T_amb_diseno=303.55 K, motor SOLO TeqpAdapter, m_b=1.0 kg/s. eta_t 0.80-0.90 y
eta_p 0.70-0.80 (rangos ya usados en rondas anteriores, sin cambios). P_alta
2800-3300 kPa, igual que en Fase 2.

Estructura: 59 "columnas" = combinaciones de todo MENOS P_baja (15 de la malla
principal x_b x eps_cond, 32 de la submalla eps_hrvg x eps_reg, 8 de eta_t x
eta_p, 4 de P_alta). Cada columna se recorre con una escalera de 7 valores de
P_baja (nivel 1, grueso) y luego dos rondas de refinamiento adaptativo
(niveles 2 y 3) que estrechan el bracket del cruce O2=0 hasta ovilizar el
P_baja minimo que da KALINA en esa columna.
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
N_WORKERS = 4
LOTE = 20
S_PT = 19.0                      # s/punto de pared medido (4 workers, ronda 4)
ESCALERA_1 = (650., 850., 1100., 1450., 1850., 2400., 2700.)
RATIO_MAX = 0.90                # tope de P_baja = 0.90 * P_alta
X_B_GRID = (0.40, 0.425, 0.45, 0.475, 0.50)
EPS_COND_GRID = (0.75, 0.80, 0.85)
EPS_HR_REGS = ((0.75, 0.75), (0.75, 0.80), (0.75, 0.85), (0.80, 0.75),
               (0.85, 0.75), (0.85, 0.80), (0.85, 0.85), (0.80, 0.85))
ETAS = ((0.80, 0.70), (0.80, 0.80), (0.90, 0.70), (0.90, 0.80))
P_ALTAS = (2800., 3300.)
# Celdas donde se cruzan eta_t/eta_p (grupo C) y P_alta (grupo D): la peor y la
# intermedia de la malla principal, elegidas por ser las que definen la
# frontera KALINA con eps_cond=0.85 y con eps_cond=0.80.
CELDA_ETA = ((0.50, 0.85), (0.45, 0.80))
SIN_PB = ("P_alta", "x_b", "eta_t", "eta_p", "eps_hrvg", "eps_reg", "eps_cond")


def cargar_r2():
    """ronda2_pbaja por ruta (la carpeta lleva guiones -> no importable)."""
    ruta = Path(__file__).resolve().parent / "ronda2_pbaja.py"
    spec = importlib.util.spec_from_file_location("ronda2_pbaja", ruta)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def columnas() -> list:
    """59 combinaciones de todo menos P_baja (base de la ronda 4)."""
    r2 = cargar_r2()
    base = dict(r2.BASE, T_fuente=470.0, T_sumidero=300.032917, m_b=1.0)
    cols, vistas = [], set()

    def agregar(**kw):
        c = dict(base, **kw)
        k = r2.tupla(dict(c, P_baja=0.0))
        if k not in vistas:
            vistas.add(k)
            cols.append(c)

    def malla(eh, er, xbs, ecs, pa=3000., et=0.85, ep=0.75):
        for xb in xbs:
            for ec in ecs:
                agregar(P_alta=pa, x_b=xb, eps_hrvg=eh, eps_reg=er,
                        eps_cond=ec, eta_t=et, eta_p=ep)

    malla(0.80, 0.80, X_B_GRID, EPS_COND_GRID)                    # A: principal
    for eh, er in EPS_HR_REGS:                                   # B: efectividades
        malla(eh, er, (0.45, 0.50), (0.80, 0.85))
    for et, ep in ETAS:                                          # C: eta_t x eta_p
        for xb, ec in CELDA_ETA:
            agregar(P_alta=3000., x_b=xb, eps_hrvg=0.80, eps_reg=0.80,
                    eps_cond=ec, eta_t=et, eta_p=ep)
    for pa in P_ALTAS:                                           # D: P_alta
        for xb, ec in CELDA_ETA:
            agregar(P_alta=pa, x_b=xb, eps_hrvg=0.80, eps_reg=0.80,
                    eps_cond=ec, eta_t=0.85, eta_p=0.75)
    return cols


def combo(col: dict, pb: float) -> dict:
    """Punto completo de la columna `col` al valor de P_baja `pb` (con tope)."""
    return dict(col, P_baja=min(float(pb), RATIO_MAX * col["P_alta"]))


def clave(col: dict) -> tuple:
    """Identificador de la columna: todo menos P_baja, a 3 decimales."""
    return tuple(round(float(col[v]), 3) for v in SIN_PB)


def nivel1() -> list:
    """Escalera gruesa completa sobre las 59 columnas."""
    return [combo(c, pb) for c in columnas() for pb in ESCALERA_1]


def puntos_por_columna() -> dict:
    """{clave de columna: [(P_baja, O2_margen) convergentes]} de lo ya calculado.

    Filtra el CSV a las filas de ESTA ronda (efectividades en [0.75, 0.85] y
    x_b >= 0.40), de modo que las 184 filas de las rondas 1-3, que vivian con
    eps_hrvg=0.85/eps_reg=0.75 y eps_cond hasta 0.95, no se confundan con las
    columnas de la ronda 4 al armar el refinamiento adaptativo.
    """
    df = pd.read_csv(CSV)
    df = df[(df["eps_hrvg"].between(0.75, 0.85))
            & (df["eps_reg"].between(0.75, 0.85))
            & (df["eps_cond"].between(0.75, 0.85)) & (df["x_b"] >= 0.40)]
    por_col: dict = {}
    for _, r in df.iterrows():
        k = tuple(round(float(r[v]), 3) for v in SIN_PB)
        o2 = r["O2_margen"]
        if bool(r["convergio"]) and o2 is not None and not pd.isna(o2):
            por_col.setdefault(k, []).append((round(float(r["P_baja"]), 1),
                                              float(o2)))
    return por_col


def refinado() -> list:
    """Niveles 2/3: 2 puntos por columna dentro del bracket O2=0 mas ancho."""
    por_col = puntos_por_columna()
    out = []
    for c in columnas():
        pts = sorted(por_col.get(clave(c), []))
        brackets = [(p1, p2) for (p1, m1), (p2, m2) in zip(pts, pts[1:])
                    if m1 * m2 < 0]
        if brackets:
            p1, p2 = max(brackets, key=lambda b: b[1] - b[0])
            out += [combo(c, p1 + f * (p2 - p1)) for f in (0.35, 0.65)]
        elif pts and pts[0][1] > 0:      # ya KALINA en el piso de la escalera
            out.append(combo(c, max(50.0, 0.60 * pts[0][0])))
    return out
