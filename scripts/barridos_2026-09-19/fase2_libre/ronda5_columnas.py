"""Fase 2, ronda 5 (tarea 2026-09-29-fase2-ronda5-xb-alto) — esquema de
exploracion de la region NUNCA tocada en Fase 2: x_b alto (0.70-0.85), la zona
de mayor eficiencia segun Karimi & Ahmad (2016) para el KCS-11 real.

Hallazgo estructural medido ANTES de fijar la rejilla (sondas de esta tarea, no
registradas en el CSV): con el ancla FIJA de Fase 2 (T_fuente=470.0 K) el ciclo
NO CIERRA para x_b >= 0.70 si P_alta <= 3300 kPa. La razon es termodinamica: el
punto de rocio T_dew(P_alta, x_b) sube al subir x_b (436.7 K a 3 MPa con
x_b=0.80) y se pega al ancla T_fuente=470 K; el HRVG entrega entonces un estado
2 practicamente saturado/supercalentado, el separador (flash ideal) no tiene
campana que repartir y el solver muere con PropertyRangeError. Por eso esta
ronda tiene DOS ejes de P_alta:

  MURO      2800-3300 kPa (eje nominal del TASK, punto 6). Se espera
            NO_CONVERGIO casi sistematico; se registra igual (constraint 3) y es
            la evidencia de que el muro existe.
  EXTENSION 3600-4500 kPa (techo autorizado por el TASK, punto 6: "hasta un
            techo de 4500 kPa ... si ayuda a encontrar KALINA ... reportalo como
            hallazgo"). Es el unico eje donde el ciclo cierra en x_b alto; se
            documenta explicito en el reporte como eje secundario NECESARIO,
            nunca como sustituto silencioso del nominal.

`x_b` en {0.70, 0.75, 0.80, 0.85} (paso 0.05, punto 2 del TASK); `P_baja` es la
palanca principal (punto 5) y se barre amplia; efectividades en [0.75, 0.85]
(punto 3) con centro 0.80; eta_t/eta_p 0.80-0.90 / 0.70-0.80 (punto 4).

Anti-duplicado: reutiliza `ronda2_pbaja.leer_probadas()` (8-tuplo a 3
decimales, leido de TODOS los CSV de fase2_libre). La region x_b >= 0.70 es
nueva (el maximo historico es 0.50), asi que el filtro solo descarta repeticiones
INTERNAS de la tanda y refundidos de nivel 2/3.
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
DIAG = CARPETA / "ronda5_diagnostico.csv"     # margenes O1/O2/S5/O5, companion
N_WORKERS = 4
LOTE = 10
S_PT = 45.0             # s/punto de pared medio medido (converge ~70 s, muro ~5 s)

X_B_GRID = (0.70, 0.75, 0.80, 0.85)           # TASK punto 2, paso 0.05
P_ALTA_MURO = (2800., 3000., 3300.)           # TASK punto 6, eje nominal
P_ALTA_EXT = (3600., 4000., 4400., 4500.)     # TASK punto 6, techo 4500 kPa
P_BAJA_MURO = (1500., 2500.)                  # 2 puntos basta para ver el muro
P_BAJA_EXT = (1000., 1600., 2200., 2800., 3400., 4000.)
RATIO_MAX = 0.90                              # mismo tope P_baja < 0.9*P_alta
ETA_T, ETA_P = 0.85, 0.75
EPS_CENTRO = 0.80
SIN_PB = ("P_alta", "x_b", "eta_t", "eta_p", "eps_hrvg", "eps_reg", "eps_cond")
ESQUEMA_CSV = ("T_fuente", "T_sumidero", "P_alta", "P_baja", "x_b", "m_b",
               "eta_t", "eta_p", "eps_hrvg", "eps_reg", "eps_cond", "T_sat_L",
               "T9_amb", "O2_margen", "convergio", "clasificacion", "eta",
               "Wnet", "mensaje")


def cargar_r2():
    """ronda2_pbaja por ruta (la carpeta lleva guiones -> no importable)."""
    ruta = Path(__file__).resolve().parent / "ronda2_pbaja.py"
    spec = importlib.util.spec_from_file_location("ronda2_pbaja", ruta)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def base_centro() -> dict:
    """Base de la ronda: ancla fija + efectividades/etas centro del rango."""
    r2 = cargar_r2()
    return dict(r2.BASE, T_fuente=470.0, T_sumidero=300.032917, m_b=1.0,
                eta_t=ETA_T, eta_p=ETA_P, eps_hrvg=EPS_CENTRO,
                eps_reg=EPS_CENTRO, eps_cond=EPS_CENTRO)


def combo(col: dict, pb: float) -> dict:
    """Punto completo con P_baja topado a 0.90*P_alta (misma regla de ronda 4)."""
    return dict(col, P_baja=min(float(pb), RATIO_MAX * col["P_alta"]))


def clave_col(col: dict) -> tuple:
    """Clave de columna: todo menos P_baja, a 3 decimales (misma de ronda 4)."""
    return tuple(round(float(col[v]), 3) for v in SIN_PB)


def nivel1() -> list:
    """Rejilla gruesa: muro (eje nominal) + extension (unico eje que cierra)."""
    base = base_centro()
    out = []
    for xb in X_B_GRID:
        for pa in P_ALTA_MURO:
            for pb in P_BAJA_MURO:
                out.append(combo(dict(base, P_alta=pa, x_b=xb), pb))
        for pa in P_ALTA_EXT:
            for pb in P_BAJA_EXT:
                out.append(combo(dict(base, P_alta=pa, x_b=xb), pb))
    return out


def leer_diag() -> pd.DataFrame:
    """Diagnostico de la ronda 5 (companion), vacio si aun no existe."""
    cols = list(SIN_PB) + ["P_baja", "margen_O2", "margen_O1", "margen_S5",
                           "convergio", "clasificacion", "eta"]
    if not DIAG.exists():
        return pd.DataFrame(columns=cols)
    return pd.read_csv(DIAG)


def por_columna() -> dict:
    """{clave de columna: [(P_baja, margen_O2, margen_O1) convergentes]}."""
    df = leer_diag()
    out: dict = {}
    if df.empty:
        return out
    ok = df[df["convergio"].astype(bool) & df["margen_O2"].notna()]
    for _, r in ok.iterrows():
        k = tuple(round(float(r[v]), 3) for v in SIN_PB)
        out.setdefault(k, []).append((round(float(r["P_baja"]), 1),
                                      float(r["margen_O2"]),
                                      float(r["margen_O1"])))
    return out


def nivel2(etas=((ETA_T, ETA_P),)) -> list:
    """Refinamiento del bracket O2=0 en las columnas de la extension.

    Para cada columna (P_alta, x_b, eta_t, eta_p, efectividades centro) busca el
    bracket mas ancho donde O2 cambia de signo y devuelve 2 puntos interiores; si
    ya es KALINA en el piso de la escalera, prueba mas abajo (0.60*P_baja_min).
    """
    por_col, base = por_columna(), base_centro()
    out = []
    for xb in X_B_GRID:
        for pa in P_ALTA_EXT:
            for et, ep in etas:
                c = dict(base, P_alta=pa, x_b=xb, eta_t=et, eta_p=ep)
                pts = sorted(por_col.get(clave_col(c), []))
                brackets = [(p1, p2) for (p1, m1, _), (p2, m2, _)
                            in zip(pts, pts[1:]) if m1 * m2 < 0]
                if brackets:
                    p1, p2 = max(brackets, key=lambda b: b[1] - b[0])
                    out += [combo(c, p1 + f * (p2 - p1)) for f in (0.35, 0.65)]
                elif pts and pts[0][1] > 0:
                    out.append(combo(c, max(50.0, 0.60 * pts[0][0])))
    return out


def nivel3() -> list:
    """Palancas de operacion en la frontera O2 de cada x_b (motor del hallazgo).

    Hallazgo de nivel 1: para cerrar O2 hay que subir P_baja hasta ~3600-4000,
    lo que deja una relacion de presiones minuscula y hunde el eta. La pregunta
    util es si alguna palanca autorizada mueve la frontera de O2 hacia P_baja
    mas bajo SIN romperla:

      eps_cond  palanca directa de O2 (el propio mensaje del criterio lo dice:
                "aumentar eps_cond"). Se prueba 0.85 y 0.75 y se baja P_baja
                150/300 kPa por debajo de la frontera para perseguir eta.
      eta_t     gobierna O1 (q4=1-eta_t*(1-q4_ideal) baja al subir eta_t) y la
                eficiencia; se prueban los extremos 0.80/0.90.
      eps_hrvg/eps_reg  mueven T2 (S5), q2 (O5) y el regenerador; extremos
                0.75/0.85.

    El ancla de cada x_b es su mejor punto convergente cerca de la frontera
    (|margen_O2|<=1..2) con mayor eta; x_b=0.85 no tiene anclas y se salta.
    """
    df = leer_diag()
    out = []
    if df.empty:
        return out
    ok = df[df["convergio"].astype(bool) & df["margen_O2"].notna()]
    base = base_centro()
    for xb in X_B_GRID:
        g = ok[(ok["x_b"] == xb) & ok["margen_O2"].between(-1.0, 2.0)]
        if g.empty:
            continue
        r = g.loc[g["eta"].idxmax()]
        pb = float(r["P_baja"])
        c = dict(base, P_alta=float(r["P_alta"]), x_b=xb,
                 eta_t=float(r["eta_t"]), eta_p=float(r["eta_p"]),
                 eps_cond=float(r["eps_cond"]))
        out += [combo(dict(c, eps_cond=0.85), pb),
                combo(dict(c, eps_cond=0.85), pb - 150.0),
                combo(dict(c, eps_cond=0.85), pb - 300.0),
                combo(dict(c, eps_cond=0.75), pb),
                combo(dict(c, eta_t=0.90), pb),
                combo(dict(c, eta_t=0.80), pb),
                combo(dict(c, eps_hrvg=0.85, eps_reg=0.85), pb),
                combo(dict(c, eps_hrvg=0.75, eps_reg=0.75), pb)]
    return out
