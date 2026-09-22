"""Ejecución en segundo plano del análisis puntual (hilo + progreso + cancelar).

`app.py` no corre el solver directamente: `iniciar` lanza un hilo de fondo que
resuelve el ciclo, la exergía y la validación, y deja el resultado en un estado
mutable guardado en `st.session_state`. `renderizar_ejecucion` muestra el panel
en curso (tiempo transcurrido, estimado, log real de iteraciones del solver y
botón Cancelar) con un fragment que repinta cada segundo, y al terminar mueve
el resultado a las claves de `st.session_state` que consume la UI.

Python no puede matar un hilo a mitad de una llamada: la cancelación es
cooperativa vía `threading.Event` que el solver chequea entre iteraciones
(`cycle_solver.resolver_ciclo(cancelar=...)`) y lanza `CicloCancelado`.
"""

from __future__ import annotations

import threading
import time

import streamlit as st

from src import ui_backend, ui_helpers
from src.cycle_solver import CicloCancelado, CicloNoConvergeError, resolver_ciclo
from src.exergy import calcular_exergia
from src.properties.adapter import PropertyRangeError
from src.restricciones import evaluar_ciclo

__all__ = ["iniciar", "hay_ejecucion", "renderizar_ejecucion"]

_CLAVE = "ejecucion_puntual"

# Estimado de tiempo total por motor [s], solo para la barra de progreso:
# iapws ~8-9 min (documentado); teqp medido ~38 s (doc: ~10-20x más rápido).
_ESTIMADO = {ui_backend.BACKEND_REAL: 8.5 * 60, ui_backend.BACKEND_TEQP: 40.0}


def _mmss(segundos: float) -> str:
    minutos, seg = divmod(int(segundos), 60)
    return f"{minutos} min {seg:02d} s" if minutos else f"{seg} s"


def _trabajar(estado: dict, backend, vals: dict) -> None:
    """Cuerpo del hilo: resuelve ciclo + exergía + validación en `estado`."""

    def progreso(evento: dict) -> None:
        estado["progreso"] = evento
        if evento["fase"] == "exterior":
            estado["log"].append(
                f"Lazo exterior (T1): iteración {evento['iteracion']}, "
                f"T1 = {evento['T1']:.2f} K, |F| = {abs(evento['residual']):.2e} K")

    try:
        resultado = resolver_ciclo(
            backend, P_alta=vals["P_alta"], P_baja=vals["P_baja"],
            T_fuente=vals["T_fuente"], T_sumidero=vals["T_sumidero"],
            x_b=vals["x_b"], m_b=vals["m_b"], eta_t=vals["eta_t"],
            eta_p=vals["eta_p"], eps_hrvg=vals["eps_hrvg"],
            eps_reg=vals["eps_reg"], eps_cond=vals["eps_cond"],
            progreso=progreso, cancelar=estado["cancelar"])
        estado["log"].append("Ciclo convergido — calculando exergía…")
        exergia = calcular_exergia(
            resultado, backend, T_fuente=vals["T_fuente"],
            T_sumidero=vals["T_sumidero"], T0=vals["T0"], P0=vals["P0"])
        estado["log"].append("Validando restricciones…")
        validacion = evaluar_ciclo(
            backend, resultado, P_alta=vals["P_alta"], P_baja=vals["P_baja"],
            T_fuente=vals["T_fuente"], T_sumidero=vals["T_sumidero"],
            x_b=vals["x_b"], m_b=vals["m_b"], eps_hrvg=vals["eps_hrvg"],
            eps_reg=vals["eps_reg"], eps_cond=vals["eps_cond"],
            T_amb_diseno=vals["T_amb_diseno"])
        estado["resultado"] = {"ciclo": resultado, "exergia": exergia,
                               "validacion": validacion}
        estado["log"].append("Listo.")
    except CicloCancelado:
        estado["cancelado"] = True
    except (CicloNoConvergeError, PropertyRangeError) as exc:
        estado["error"] = exc
    except Exception as exc:  # se reporta en la UI, no se traga en silencio
        estado["error"] = exc
    finally:
        estado["terminado"] = True


def iniciar(backend_sel: str, vals: dict) -> None:
    """Lanza la corrida en un hilo de fondo y registra su estado en sesión."""
    backend, nombre, aviso = ui_backend.construir_backend(backend_sel, vals["x_b"])
    vals = dict(vals)
    # Criterio O2 sin margen (2026-09-20): desmarcado → T_amb_diseno = T_sumidero.
    if not vals.get("aplica_margen_o2", True):
        vals["T_amb_diseno"] = vals["T_sumidero"]
    for clave in ui_helpers.CLAVES_RESULTADO:
        st.session_state.pop(clave, None)
    estado = {
        "cancelar": threading.Event(),
        "progreso": None,
        "log": [f"Motor: {nombre}. Iniciando…"],
        "inicio": time.time(),
        "resultado": None,
        "error": None,
        "cancelado": False,
        "terminado": False,
        "nombre_backend": nombre,
        "aviso": aviso,
        "parametros": ui_helpers.dict_parametros(vals),
    }
    hilo = threading.Thread(target=_trabajar, args=(estado, backend, vals),
                            daemon=True)
    estado["hilo"] = hilo
    st.session_state[_CLAVE] = estado
    hilo.start()


def hay_ejecucion() -> bool:
    """True si hay una corrida en curso (para no lanzar una segunda)."""
    estado = st.session_state.get(_CLAVE)
    return estado is not None and not estado["terminado"]


def renderizar_ejecucion() -> bool:
    """Panel de la corrida en curso. Devuelve True mientras siga corriendo."""
    estado = st.session_state.get(_CLAVE)
    if estado is None:
        return False
    if estado["terminado"]:
        _finalizar(estado)
        return False
    _panel_en_curso()
    return True


@st.fragment(run_every=1.0)
def _panel_en_curso() -> None:
    """Repinta cada segundo: tiempo, estimado, log y botón Cancelar."""
    estado = st.session_state.get(_CLAVE)
    if estado is None:
        return
    if estado["terminado"]:
        st.rerun()
    transcurrido = time.time() - estado["inicio"]
    if estado["aviso"]:
        st.warning(estado["aviso"])
    st.info(f"⏳ Resolviendo el ciclo con **{estado['nombre_backend']}** — "
            f"tiempo transcurrido: **{_mmss(transcurrido)}**.")
    prog = estado["progreso"]
    if prog is not None:
        detalle = (f"T1 = {prog['T1']:.2f} K" if prog["fase"] == "exterior"
                   else f"T10 = {prog['T10']:.2f} K")
        st.caption(f"Última iteración: lazo {prog['fase']}, "
                   f"iteración {prog['iteracion']}, {detalle}.")
    estimado = _ESTIMADO.get(estado["nombre_backend"])
    if estimado:
        st.progress(min(transcurrido / estimado, 0.97))
        st.caption(f"Tiempo total estimado: ~{_mmss(estimado)} "
                   "(aproximado; depende de la convergencia).")
    st.markdown("**Registro de ejecución**")
    st.code("\n".join(estado["log"][-12:]), language=None)
    if st.button("Cancelar corrida", key="btn_cancelar_puntual"):
        estado["cancelar"].set()
        st.warning("Cancelando… se detendrá al cerrar la iteración en curso.")


def _finalizar(estado: dict) -> None:
    """Mueve el resultado a session_state o reporta cancelación/error."""
    st.session_state.pop(_CLAVE, None)
    if estado["cancelado"]:
        for clave in ui_helpers.CLAVES_RESULTADO:
            st.session_state.pop(clave, None)
        st.warning("⚠️ Corrida **cancelada**. No se guardaron resultados.")
        return
    if estado["error"] is not None:
        for clave in ui_helpers.CLAVES_RESULTADO:
            st.session_state.pop(clave, None)
        exc = estado["error"]
        if isinstance(exc, CicloNoConvergeError):
            st.warning("⚠️ El ciclo **no convergió** con estos parámetros: "
                       f"{exc}. Pruebe con otros valores, por ejemplo T_fuente "
                       "más alta u otras efectividades.")
        elif isinstance(exc, PropertyRangeError):
            st.warning("⚠️ Algún estado quedó **fuera del rango válido** del "
                       f"motor de propiedades: {exc}. Revise presiones, "
                       "temperaturas y composición.")
        else:
            st.error(f"Error inesperado al resolver el ciclo: {exc}")
        return
    res = estado["resultado"]
    st.session_state["resultado_ciclo"] = res["ciclo"]
    st.session_state["resultado_exergia"] = res["exergia"]
    st.session_state["resultado_validacion"] = res["validacion"]
    st.session_state["parametros"] = estado["parametros"]
    st.session_state["backend_nombre"] = estado["nombre_backend"]
    st.success("✅ Simulación completada. Resultados abajo.")
