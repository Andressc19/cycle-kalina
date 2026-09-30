"""Diagnostico de la rama fisica de la salida de turbina — tarea
2026-09-24-rama-turbina-y-estabilidad, Parte 1.

Pregunta: en (x_b=0.60, P_alta=4000, T_fuente=394) la expansion isoentropica
h4s = backend.h(P_baja, s=s3, x=x3) (src/components/turbina.py:35) salta entre
dos ramas al mover P_baja 0.25 kPa cerca de 424 kPa. Solo una rama es fisica.

1. Resolver el ciclo con TeqpAdapter(x=0.60) en P_baja=423.914831 y
   424.169832 (evaluaciones_margen.csv); guardar s3, x3, h3, h4s, h4, T4.
2. Barrido de la expansion aislada: h(P, s=s3, x=x3) y T_from_Ps(P, s3, x3)
   para P 419.0..429.0 cada 0.25 kPa (+424.169832); registrar donde salta.
3. Monotonia de s(T) a P=424.0, x=x3, T 250..350 K cada 0.5 K.
4. Referencia con el motor real (AmmoniaWaterAdapter): h(P, s=s3, x=x3) y
   T_from_Ps(P, s3, x3) SOLO en P ∈ {420.0, 422.0, 424.169832}; captura
   excepciones y registra tiempo.
5. Veredicto: la rama de teqp que coincide con el motor real (±2 kJ/kg en h,
   ±0.5 K en T) es la fisica. Para tener AMBAS ramas en cada P_ref se escanea
   s(T) fino y se refinan todas las raices de s(T,x3)=s3.

No modifica src/; solo escribe en resultados/2026-09-24_rama_turbina/.
"""
from __future__ import annotations

import csv
import sys
import time
from pathlib import Path

import numpy as np
from scipy.optimize import brentq

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))

from calibracion_elsayed_malla import ETA_P, ETA_T, M_B, T_SUMIDERO  # noqa: E402
from src.cycle_solver import CicloNoConvergeError, resolver_ciclo  # noqa: E402
from src.properties.adapter import PropertyRangeError  # noqa: E402
from src.properties.teqp_adapter import TeqpAdapter  # noqa: E402

OUT = REPO / "resultados" / "2026-09-24_rama_turbina"
EPS = (0.85, 0.80, 0.85)
X_B, P_ALTA, T_FUENTE = 0.60, 4000.0, 394.0
P_B1, P_B2 = 423.914831, 424.169832       # par del salto (evaluaciones_margen.csv)
P_REF = (420.0, 422.0, 424.169832)        # presiones de la referencia con motor real
EXC = (CicloNoConvergeError, PropertyRangeError, ValueError,
       RuntimeError, NotImplementedError)


def log(msg): print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)  # noqa: E731


def escribir(nombre, cols, filas):
    with open(OUT / nombre, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader(); w.writerows(filas)


def resolver(P_baja, backend):
    return resolver_ciclo(backend, P_alta=P_ALTA, P_baja=P_baja, T_fuente=T_FUENTE,
                          T_sumidero=T_SUMIDERO, x_b=X_B, m_b=M_B, eta_t=ETA_T,
                          eta_p=ETA_P, eps_hrvg=EPS[0], eps_reg=EPS[1],
                          eps_cond=EPS[2])


def trazo(backend, s3, x3, P):
    """Igual llamada que turbina.py: h4s y T4s de la expansion isoentropica."""
    h4s = backend.h(P, s=s3, x=x3)
    T4s = backend.T_from_Ps(P, s3, x3)
    fase, q = backend.fase_de(P, T4s, x3)
    return h4s, T4s, fase, q


def raices_finas(backend, s3, x3, P):
    """Todas las raices de s(T,P,x3)=s3 en T∈[260,300] K, paso 0.05 K.

    Refina cada cambio de signo de f(T)=s(T,P,x3)-s3 con brentq: resuelve el
    problema real de raices multiples de la inversion T_from_Ps.
    """
    ceros = []
    prev = backend.s(P, T=260.0, x=x3) - s3
    for i in range(1, 801):
        T = 260.0 + 0.05 * i
        f = backend.s(P, T=T, x=x3) - s3
        if f == 0.0:
            ceros.append(T)
        elif prev * f < 0.0:
            a, b = T - 0.05, T
            try:
                ceros.append(brentq(lambda t: backend.s(P, T=t, x=x3) - s3,
                                    a, b, xtol=1e-7))
            except Exception:
                pass
        prev = f
    return [(t, backend.h(P, T=t, x=x3), backend.fase_de(P, t, x3)[0])
            for t in ceros]


def paso1():
    log("paso 1: resolver el ciclo en el par del salto")
    filas, guardados = [], {}
    for P in (P_B1, P_B2):
        t0 = time.perf_counter()
        res = resolver(P, TeqpAdapter(x=X_B))
        e3, e4 = res["estados"]["e3"], res["estados"]["e4"]
        h4s, T4s, fase, q = trazo(TeqpAdapter(x=X_B), e3.s, e3.x, P)
        guardados[P] = (e3.s, e3.x)
        filas.append(dict(P_baja=P, s3=e3.s, x3=e3.x, h3=e3.h, h4s=h4s,
                          T4s=T4s, fase4s=fase, q4s=q, h4=e4.h, T4=e4.T,
                          eta=res["eta"], tiempo_s=round(time.perf_counter() - t0, 1)))
        log(f"  P={P}: s3={e3.s:.6f} x3={e3.x:.6f} h4s={h4s:.3f} "
            f"(T4s={T4s:.3f}, {fase}) h4={e4.h:.3f} T4={e4.T:.3f} eta={res['eta']:.6f}")
    escribir("solucion_dos_puntos.csv", list(filas[0].keys()), filas)
    return guardados


def paso2(backend, s3, x3):
    log("paso 2: barrido de la expansion aislada 419.0..429.0 (0.25 kPa)")
    filas, prev_h = [], None
    for P in list(np.arange(419.0, 429.0 + 1e-9, 0.25)) + [P_REF[2]]:
        h4s, T4s, fase, q = trazo(backend, s3, x3, float(P))
        salto = "" if prev_h is None else round(abs(h4s - prev_h), 6)
        filas.append(dict(P=round(float(P), 6), h4s=round(h4s, 6),
                          T4s=round(T4s, 6), fase=fase,
                          q=round(q, 6), salto_h4s=salto))
        prev_h = h4s
    escribir("expansion_P.csv", ("P", "h4s", "T4s", "fase", "q", "salto_h4s"), filas)
    saltos = [f["P"] for f in filas if f["salto_h4s"] != "" and f["salto_h4s"] > 10.0]
    log(f"  saltos |d(h4s)|>10 kJ/kg en P={saltos}")


def paso3(backend, x3):
    log("paso 3: monotonia de s(T) a P=424.0, x=x3, T 250..350 cada 0.5 K")
    filas, prev = [], None
    for i in range(201):
        T = 250.0 + 0.5 * i
        s = backend.s(424.0, T=T, x=x3)
        h = backend.h(424.0, T=T, x=x3)
        fase = backend.fase_de(424.0, T, x3)[0]
        ds = "" if prev is None else s - prev
        filas.append(dict(T=round(T, 1), s=round(s, 6), h=round(h, 4), fase=fase,
                          ds="" if ds == "" else round(ds, 6),
                          crece="" if ds == "" else ("si" if ds >= 0.0 else "NO")))
        prev = s
    escribir("s_de_T.csv", ("T", "s", "h", "fase", "ds", "crece"), filas)
    no_mono = [f["T"] for f in filas if f["crece"] == "NO"]
    log(f"  s(T) estrictamente creciente: {not no_mono}; caidas en T={no_mono}")


def paso4(s3, x3):
    log("paso 4: referencia con el motor real (AmmoniaWaterAdapter) en 3 P")
    from src.properties.ammonia_water_adapter import AmmoniaWaterAdapter  # noqa: PLC0415
    real = AmmoniaWaterAdapter(x=X_B)
    filas = []
    for P in P_REF:
        fila = dict(P=P, h_real="", T_real="", tiempo_h_s="", tiempo_T_s="", error="")
        for campo, fn in (("h_real", lambda: real.h(P, s=s3, x=x3)),
                          ("T_real", lambda: real.T_from_Ps(P, s3, x3))):
            t0 = time.perf_counter()
            try:
                fila[campo] = round(float(fn()), 6)
            except EXC as exc:
                fila["error"] = ((fila["error"] + " | " if fila["error"] else "")
                                 + f"{campo}: {type(exc).__name__}: {exc}")
            fila["tiempo_h_s" if campo == "h_real" else "tiempo_T_s"] = \
                round(time.perf_counter() - t0, 2)
        filas.append(fila)
        log(f"  P={P}: h_real={fila['h_real']} T_real={fila['T_real']} "
            f"t_h={fila['tiempo_h_s']}s t_T={fila['tiempo_T_s']}s "
            f"err={fila['error'][:60]}")
    return filas


def paso5(backend, s3, x3, real_filas):
    log("paso 5: ramas de teqp en cada P_ref y veredicto")
    filas, fisica = [], []
    for r in real_filas:
        P = r["P"]
        raices = raices_finas(backend, s3, x3, P)
        rama_A = [z for z in raices if 271.0 <= z[0] <= 274.5]
        rama_B = [z for z in raices if 279.0 <= z[0] <= 285.0]
        a = max(rama_A, key=lambda z: z[1]) if rama_A else None
        b = rama_B[0] if rama_B else None
        if r["error"] or r["h_real"] == "":
            va = vb = "no evaluable"
            fisica.append("no_evaluable")
        else:
            va = ("si" if a is not None and abs(a[1] - r["h_real"]) <= 2.0
                  and abs(a[0] - r["T_real"]) <= 0.5 else "no")
            vb = ("si" if b is not None and abs(b[1] - r["h_real"]) <= 2.0
                  and abs(b[0] - r["T_real"]) <= 0.5 else "no")
            fisica.append("rama_B" if vb == "si" else "rama_A" if va == "si"
                          else "ninguna")
        filas.append(dict(P=P,
                          h_ramaA="" if a is None else round(a[1], 4),
                          T_ramaA="" if a is None else round(a[0], 4),
                          faseA="" if a is None else a[2],
                          h_ramaB="" if b is None else round(b[1], 4),
                          T_ramaB="" if b is None else round(b[0], 4),
                          faseB="" if b is None else b[2],
                          h_real=r["h_real"], T_real=r["T_real"],
                          coincide_ramaA=va, coincide_ramaB=vb,
                          tiempo_h_s=r["tiempo_h_s"], tiempo_T_s=r["tiempo_T_s"],
                          error=r["error"]))
        log(f"  P={P}: A=(h={filas[-1]['h_ramaA']}, T={filas[-1]['T_ramaA']}, "
            f"{filas[-1]['faseA']}) B=(h={filas[-1]['h_ramaB']}, "
            f"T={filas[-1]['T_ramaB']}, {filas[-1]['faseB']}) "
            f"real=(h={filas[-1]['h_real']}, T={filas[-1]['T_real']}) "
            f"-> A={va} B={vb}")
    nB = fisica.count("rama_B")
    veredicto = ("rama_B" if nB >= 2 and nB > fisica.count("rama_A")
                 else "rama_A" if fisica.count("rama_A") >= 2 else "inconcluyente")
    for fi in filas:
        fi["veredicto"] = veredicto
    escribir("motor_real.csv", list(filas[0].keys()), filas)
    log(f"  VEREDICTO: {veredicto} (por P: {fisica})")
    return dict(veredicto=veredicto, por_punto=list(zip(P_REF, fisica)))


def principal():
    OUT.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    guardados = paso1()
    backend = TeqpAdapter(x=X_B)
    s3, x3 = guardados[P_B2]
    paso2(backend, s3, x3)
    paso3(backend, x3)
    paso5(backend, s3, x3, paso4(s3, x3))
    log(f"Parte 1 completa en {time.time() - t0:.0f}s; CSV en {OUT}")


if __name__ == "__main__":
    principal()