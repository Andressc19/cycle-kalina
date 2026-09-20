"""Fase 3 (Husavik) — helpers comunes del barrido de sensibilidad FINAL.

Tarea 2026-09-20-fase3-sensibilidad-final. Contiene:
- El ancla confirmada con el motor real (eta=0.12730, KALINA) y el piso de
  diseno O2 de Islandia (T_amb_diseno=283.15 K) — valores fijos, el director
  los decidio y no se cambian.
- `margenes`: margenes de los tres criterios que pueden decidir la
  clasificacion cerca de una frontera (O1: q4-0.90; O2: T_sat_L-T9_amb;
  S5: T_fuente-T2) y `criterio_ligante` (el que decide la clasificacion del
  punto, o el mas cerca de su borde si el punto es KALINA).
- `resolver_punto`: resuelve + clasifica un punto con TeqpAdapter y devuelve
  la fila completa en el esquema de `tabla_barrido` (src/sensitivity.py)
  mas los margenes y la candidatura a spot-check con motor real.

NOTA sobre la API de barrido: se usan Fijo/Barrido/generar_combinaciones de
src/sensitivity.py (validados); no se llama a `ejecutar_barrido` porque esa
funcion evalua O2 con T_amb_diseno=303.55 (default de evaluar_ciclo), el piso
tropical heredado que esta tarea descarta explicitamente para Husavik.

NO modifica codigo de produccion. NO toca fase2_libre/ (tarea paralela).
"""

from __future__ import annotations

from src.components.condensador import resolver as resolver_cond
from src.cycle_solver import CicloNoConvergeError, resolver_ciclo
from src.properties.adapter import PropertyRangeError
from src.restricciones import evaluar_ciclo

T_AMB_DISENO = 283.15          # piso realista de diseno para Islandia (10 C)

# Centro/ANCLA confirmada con motor real (NO cambiar): KALINA, eta=0.12730.
CENTRO = dict(P_alta=3300.0, P_baja=690.0, x_b=0.82, T_fuente=394.15,
              T_sumidero=278.15, m_b=1.0, eta_t=0.90, eta_p=0.80,
              eps_hrvg=0.85, eps_reg=0.75, eps_cond=0.95)

VARIABLES = ("T_fuente", "T_sumidero", "P_alta", "P_baja", "x_b", "m_b",
             "eta_t", "eta_p", "eps_hrvg", "eps_reg", "eps_cond")

# Esquema `tabla_barrido` + margenes del criterio ligante + spot-check.
COLUMNAS = list(VARIABLES) + [
    "convergio", "clasificacion", "eta", "Wnet", "mensaje",
    "margen_O1", "margen_O2", "margen_S5", "criterio_ligante",
    "margen_ligante", "spot_check",
    "motor_confirmado", "motor_real_clasificacion", "motor_real_eta"]

# Umbrales de spot-check (margen del criterio ligante a menos de...):
# O1 en titulo q4 (adimensional, 0.02), O2 y S5 en K (1.5 K).
UMBRALES = {"O1": 0.02, "O2": 1.5, "S5": 1.5}

NOMBRES_VAR = {"P_baja": "P_baja [kPa]", "eps_cond": "eps_cond [-]",
               "eps_reg": "eps_reg [-]", "x_b": "x_b (NH3) [-]",
               "eta_t": "eta_turbina [-]"}
ETIQUETA_CSV = {"P_baja": "P_baja", "eps_cond": "eps_cond",
                "eps_reg": "eps_reg", "x_b": "x_b", "eta_t": "eta_t"}


def margenes(backend, resultado, *, P_baja, x_b, T_fuente, T_sumidero,
             eps_cond, m_b) -> dict:
    """Margenes O1/O2/S5 del punto ya resuelto (positivo = dentro del criterio).

    O1: q4 - 0.90 (titulo a la salida de la turbina, umbral 0.90).
    O2: T_sat_L - T9_amb, con el condensador re-resuelto al peor caso
        max(T_sumidero, T_amb_diseno) (misma regla que `verificar_operativos`).
    S5: T_fuente - T2 (salida del HRVG bajo la fuente).
    """
    e = resultado["estados"]
    _, q4 = backend.fase_de(P_baja, e["e4"].T, e["e4"].x)
    m_o1 = q4 - 0.90
    t_amb = max(T_sumidero, T_AMB_DISENO)
    est9, _ = resolver_cond(e["e8"], backend, T_sumidero=t_amb,
                            eps=eps_cond, m=m_b)
    m_o2 = backend.bubble_point(P_baja, x_b) - est9.T
    m_s5 = T_fuente - e["e2"].T
    return {"O1": m_o1, "O2": m_o2, "S5": m_s5}


def criterio_ligante(m: dict, codigo_principal: str | None
                     ) -> tuple[str | None, float | None]:
    """(criterio, margen) que decide la clasificacion del punto.

    Si el punto tiene una falla principal cuyo codigo es O1/O2/S5, ese es el
    ligante con su margen. Si el punto es KALINA (sin fallas), el ligante es
    el criterio proporcionalmente mas cerca de su borde. Con cualquier otra
    falla principal (p.ej. S4), no aplica spot-check O1/O2/S5: (None, None).
    """
    if codigo_principal in UMBRALES:
        return codigo_principal, m[codigo_principal]
    if codigo_principal is None:
        lig = min(UMBRALES, key=lambda c: abs(m[c]) / UMBRALES[c])
        return lig, m[lig]
    return None, None


def _fila_no_convergio(combo: dict, mensaje: str) -> dict:
    fila = dict(combo)
    fila.update(convergio=False, clasificacion="NO_CONVERGIO", eta=None,
                Wnet=None, mensaje=mensaje[:300], margen_O1=None,
                margen_O2=None, margen_S5=None, criterio_ligante=None,
                margen_ligante=None, spot_check=False,
                motor_confirmado=None, motor_real_clasificacion="",
                motor_real_eta=None)
    return fila


def resolver_punto(combo: dict) -> dict:
    """Resuelve + clasifica un punto con TeqpAdapter (esquema tabla_barrido).

    `combo` declara las 11 variables de entrada. Todo punto probado se
    registra igual, converja o no. Usa T_amb_diseno=283.15 en la evaluacion.
    """
    from src.properties.teqp_adapter import TeqpAdapter
    backend = TeqpAdapter(x=combo["x_b"])
    try:
        resultado = resolver_ciclo(backend, **combo)
    except (CicloNoConvergeError, PropertyRangeError) as exc:
        return _fila_no_convergio(combo, str(exc))
    try:
        val = evaluar_ciclo(backend, resultado, P_alta=combo["P_alta"],
                            P_baja=combo["P_baja"], T_fuente=combo["T_fuente"],
                            T_sumidero=combo["T_sumidero"], x_b=combo["x_b"],
                            m_b=combo["m_b"], eps_hrvg=combo["eps_hrvg"],
                            eps_reg=combo["eps_reg"],
                            eps_cond=combo["eps_cond"],
                            T_amb_diseno=T_AMB_DISENO)
    except PropertyRangeError as exc:
        # Borde de dominio del motor al re-resolver el condensador en O2.
        return _fila_no_convergio(
            combo, f"evaluador O2 fuera de dominio: {exc}")
    fila = dict(combo)
    fila.update(convergio=True, clasificacion=val.clasificacion.value,
                eta=resultado["eta"], Wnet=resultado["Wnet"],
                mensaje=val.mensaje_reporte()[:300])
    try:
        m = margenes(backend, resultado, P_baja=combo["P_baja"],
                     x_b=combo["x_b"], T_fuente=combo["T_fuente"],
                     T_sumidero=combo["T_sumidero"],
                     eps_cond=combo["eps_cond"], m_b=combo["m_b"])
    except PropertyRangeError:
        fila.update(margen_O1=None, margen_O2=None, margen_S5=None,
                    criterio_ligante=None, margen_ligante=None,
                    spot_check=False, motor_confirmado=None,
                    motor_real_clasificacion="", motor_real_eta=None)
        return fila
    ligante, m_ligante = criterio_ligante(
        m, val.principal.codigo if val.principal else None)
    fila.update(margen_O1=m["O1"], margen_O2=m["O2"], margen_S5=m["S5"],
                criterio_ligante=ligante, margen_ligante=m_ligante,
                spot_check=(ligante is not None
                            and abs(m_ligante) <= UMBRALES[ligante]),
                motor_confirmado=None, motor_real_clasificacion="",
                motor_real_eta=None)
    return fila


def guardar(df, ruta) -> None:
    """Guarda un DataFrame en CSV con el esquema comun y reporta el conteo."""
    import pandas as pd
    ruta.parent.mkdir(parents=True, exist_ok=True)
    df = df[COLUMNAS]
    df.to_csv(ruta, index=False, encoding="utf-8")
    conteo = df["clasificacion"].value_counts().to_dict()
    print(f"  guardado {ruta} ({len(df)} filas): {conteo}", flush=True)