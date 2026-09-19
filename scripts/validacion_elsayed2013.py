"""Validación externa contra Elsayed et al. (2013), IJLCT 8(suppl_1) i69-i78,
doi:10.1093/ijlct/ctt020. NO toca código de producción — es un script de
análisis puntual (mismo espíritu que `diagnostico_rendimiento.py`).

Caso citado (texto del paper): P_alta=15 bar=1500 kPa, x_b=0.55,
T_fuente=373 K, T_sumidero=283 K, eta_t=eta_p=0.80, eta_reportada=11.38%.

El paper cierra HRVG/condensador/regenerador por PINCH POINT (DeltaT_min=4K),
no por efectividad como este repo (ver CONTEXT.md). Traducción aproximada
(autorizada explícitamente por el usuario, "traduce el pinch a una
efectividad o temperatura de entrada aproximada"):

- HRVG:        T2 = T_fuente - 4       (la efectividad de este repo define
                h2_ideal = h(T_fuente, P_alta, x_b), o sea eps=1 <=> T2=T_fuente,
                exactamente el mismo terminal que el pinch del paper)
- Condensador: T9 = T_sumidero + 4     (h9_ideal = h(T_sumidero, P_baja, x_b))
- Regenerador: T6 = T10 + 4            (h6_ideal = h(T10, P_alta, x5), T10 es
                                         el estado de entrada al regenerador
                                         frío -> el paper no da T10 porque su
                                         cierre no lo necesita; aquí se toma
                                         el T10 que resulte de resolver el
                                         ciclo)

P_baja no está dado por el paper (su modelo no lo necesita como input
independiente). Asunción explícita: P_baja = presión de burbuja a
(T_sumidero+4, x_b) -- la presión de condensación "de diseño" consistente con
que el condensador saque líquido saturado a esa temperatura. Es un supuesto
de ingeniería, no un dato del paper.

Método de calibración (aproximado, no un root-find exacto sobre el ciclo
completo -- sería carísimo en tiempo de cómputo con el motor real):
1. Resolver el ciclo una vez con eps de partida (0.85/0.75/0.80, los
   default del proyecto) para obtener un estado base (h1, T10, h5, x5, h8).
2. Con ese estado base, despejar eps_hrvg/eps_reg/eps_cond en forma cerrada
   de las fórmulas de CONTEXT.md para que T2/T6/T9 den los targets de arriba.
3. Resolver el ciclo otra vez con esos eps calibrados y verificar que T2/T6/T9
   quedaron cerca de los targets.
4. Backend rápido (Teqp) para calibrar, backend real (AmmoniaWater) para el
   número final que se compara contra el paper.

Resultado, metodología completa y decisión de aceptación: ver
`VALIDACION_ELSAYED2013.md` en la raíz del repo y, en el vault de Obsidian
del proyecto, `decisiones/validacion-elsayed2013-ciclo-kalina-tercero-
20260919.md`. Los eps/P_baja que resultan de esta corrida quedaron fijados
(hardcoded) en `tests/test_validacion_elsayed2013.py` — no se recalibran en
cada corrida de la suite.

Uso (con el venv del proyecto, desde la raíz):
    python scripts/validacion_elsayed2013.py
"""
from __future__ import annotations

import json
import time

from src.cycle_solver import CicloNoConvergeError, resolver_ciclo
from src.properties.adapter import PropertyRangeError
from src.properties.ammonia_water_adapter import AmmoniaWaterAdapter
from src.properties.teqp_adapter import TeqpAdapter

X_B = 0.55
T_FUENTE = 373.0
T_SUMIDERO = 283.0
P_ALTA = 1500.0
ETA_T = 0.80
ETA_P = 0.80
M_B = 1.0
PINCH = 4.0
T2_TARGET = T_FUENTE - PINCH   # 369.0
T9_TARGET = T_SUMIDERO + PINCH  # 287.0
ETA_PAPER = 0.1138


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def calibrar_P_baja(backend):
    from scipy.optimize import brentq
    f = lambda P: backend.bubble_point(P, X_B) - T9_TARGET
    # bracket: presion de burbuja crece con T, buscamos entre 50 kPa y P_alta
    P = brentq(f, 50.0, P_ALTA - 10.0, xtol=1e-4)
    return P


def resolver(backend, P_baja, eps_hrvg, eps_reg, eps_cond):
    return resolver_ciclo(
        backend, P_alta=P_ALTA, P_baja=P_baja, T_fuente=T_FUENTE,
        T_sumidero=T_SUMIDERO, x_b=X_B, m_b=M_B, eta_t=ETA_T, eta_p=ETA_P,
        eps_hrvg=eps_hrvg, eps_reg=eps_reg, eps_cond=eps_cond)


def calibrar_eps(backend, P_baja):
    log("Paso base: resolviendo con eps de partida (0.85/0.75/0.80)...")
    r0 = resolver(backend, P_baja, 0.85, 0.75, 0.80)
    e0 = r0["estados"]
    h1_0, T10_0 = e0["e1"].h, e0["e10"].T
    h5_0, x5_0 = e0["e5"].h, e0["e5"].x
    h8_0 = e0["e8"].h
    log(f"  base: T1={e0['e1'].T:.2f} T10={T10_0:.2f} T2={e0['e2'].T:.2f} "
        f"T6={e0['e6'].T:.2f} T9={e0['e9'].T:.2f} x5={x5_0:.4f}")

    h2_ideal = backend.h(P_ALTA, T=T_FUENTE, x=X_B)
    h2_target = backend.h(P_ALTA, T=T2_TARGET, x=X_B)
    eps_hrvg = (h2_target - h1_0) / (h2_ideal - h1_0)

    T6_target = T10_0 + PINCH
    h6_ideal = backend.h(P_ALTA, T=T10_0, x=x5_0)
    h6_target = backend.h(P_ALTA, T=T6_target, x=x5_0)
    eps_reg = (h5_0 - h6_target) / (h5_0 - h6_ideal)

    h9_ideal = backend.h(P_baja, T=T_SUMIDERO, x=X_B)
    h9_target = backend.h(P_baja, T=T9_TARGET, x=X_B)
    eps_cond = (h8_0 - h9_target) / (h8_0 - h9_ideal)

    eps_hrvg = min(max(eps_hrvg, 0.01), 0.999)
    eps_reg = min(max(eps_reg, 0.01), 0.999)
    eps_cond = min(max(eps_cond, 0.01), 0.999)
    log(f"  eps calibrados (1er orden): hrvg={eps_hrvg:.4f} reg={eps_reg:.4f} "
        f"cond={eps_cond:.4f}")

    log("Paso de verificacion: resolviendo con eps calibrados...")
    r1 = resolver(backend, P_baja, eps_hrvg, eps_reg, eps_cond)
    e1 = r1["estados"]
    log(f"  verif: T2={e1['e2'].T:.2f} (target {T2_TARGET}) "
        f"T6={e1['e6'].T:.2f} (target T10+4={e1['e10'].T + PINCH:.2f}) "
        f"T9={e1['e9'].T:.2f} (target {T9_TARGET})")
    log(f"  eta obtenida = {r1['eta']:.5f} ({r1['eta']*100:.3f}%) vs paper "
        f"{ETA_PAPER*100:.2f}%")
    return dict(eps_hrvg=eps_hrvg, eps_reg=eps_reg, eps_cond=eps_cond,
                resultado=r1)


def main():
    backend_rapido = TeqpAdapter(x=X_B)
    P_baja = calibrar_P_baja(backend_rapido)
    log(f"P_baja calibrada (burbuja a T={T9_TARGET}K, x={X_B}) = {P_baja:.2f} kPa")

    log("=== Calibracion con TeqpAdapter (rapido) ===")
    cal = calibrar_eps(backend_rapido, P_baja)

    salida = {
        "caso": dict(P_alta=P_ALTA, P_baja=P_baja, T_fuente=T_FUENTE,
                    T_sumidero=T_SUMIDERO, x_b=X_B, eta_t=ETA_T, eta_p=ETA_P,
                    m_b=M_B, pinch=PINCH),
        "eps_calibrados": {k: cal[k] for k in ("eps_hrvg", "eps_reg", "eps_cond")},
        "teqp": {"eta": cal["resultado"]["eta"], "Wnet": cal["resultado"]["Wnet"],
                "Qi": cal["resultado"]["Qi"]},
    }

    log("=== Corrida final con AmmoniaWaterAdapter (motor real, mas lenta) ===")
    backend_real = AmmoniaWaterAdapter(x=X_B)
    try:
        r_real = resolver(backend_real, P_baja, cal["eps_hrvg"], cal["eps_reg"],
                          cal["eps_cond"])
        e = r_real["estados"]
        log(f"  real: T2={e['e2'].T:.2f} T6={e['e6'].T:.2f} T9={e['e9'].T:.2f} "
            f"eta={r_real['eta']:.5f} ({r_real['eta']*100:.3f}%)")
        salida["real"] = {"eta": r_real["eta"], "Wnet": r_real["Wnet"],
                          "Qi": r_real["Qi"],
                          "estados": {k: dict(T=v.T, P=v.P, h=v.h, s=v.s, x=v.x,
                                              m=v.m, q=v.q, fase=v.fase)
                                     for k, v in e.items()}}
    except (CicloNoConvergeError, PropertyRangeError) as exc:
        log(f"  FALLO con motor real: {exc}")
        salida["real"] = {"error": str(exc)}

    with open("validacion_elsayed2013.json", "w", encoding="utf-8") as f:
        json.dump(salida, f, indent=2, ensure_ascii=False)
    log("Guardado validacion_elsayed2013.json")
    log("LISTO")


if __name__ == "__main__":
    main()
