"""Verificacion de la rama fisica de la salida isoentropica de turbina para los
22 KALINA de barrido_margen2k.csv — tarea 2026-09-24-rama-fisica-22-kalina.

La expansion h4s = h(P_baja, s=s3, x=x3) (turbina.py:35) puede caer en una rama
espuria del flash de teqp. Para cada punto KALINA (x_b, P_alta, T_fuente, P*)
con parametros fijos del barrido (eps 0.85/0.80/0.85, T_sumidero=283.0,
eta_t=eta_p=0.80, m_b=1):
  1. Ciclo con TeqpAdapter en P* (s3, x3, h3, T3, h4, T4, eta, Wnet) y expansion
     h4s_teqp = h(P*, s=s3, x=x3), T4s_teqp = T_from_Ps(P*, s3, x3) + fase_de.
  2. Motor real (AmmoniaWaterAdapter): h4s_real y T4s_real con mismos s3, x3.
  3. rama_fisica = |dh4s| <= 2.0 kJ/kg y |dT4s| <= 0.5 K (fijos); "no evaluable"
     si el motor real falla o el ciclo teqp no resuelve.
  4. Hasta 3 no fisicos: ciclo completo con el motor real (eta, Wnet, margen O2
     a 283.15 K, clasificacion con T_amb_diseno=283.15); si hay mas, solo listar.

Salida: resultados/2026-09-24_rama_22/rama_fisica_22.csv y REPORTE_RAMA_22.md.
No modifica src/ ni archivos existentes.
"""
from __future__ import annotations

import csv
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))

from calibracion_elsayed_malla import ETA_P, ETA_T, M_B, T_SUMIDERO  # noqa: E402
from src._cycle_loops import CicloNoConvergeError  # noqa: E402
from src.components import condensador  # noqa: E402
from src.cycle_solver import resolver_ciclo  # noqa: E402
from src.properties.adapter import PropertyRangeError  # noqa: E402
from src.properties.ammonia_water_adapter import AmmoniaWaterAdapter  # noqa: E402
from src.properties.teqp_adapter import TeqpAdapter  # noqa: E402
from src.restricciones import Clasificacion, evaluar_ciclo  # noqa: E402

SRC = REPO / "resultados" / "2026-09-24_margen2k" / "barrido_margen2k.csv"
OUT_DIR = REPO / "resultados" / "2026-09-24_rama_22"
OUT = OUT_DIR / "rama_fisica_22.csv"
REPORTE = OUT_DIR / "REPORTE_RAMA_22.md"
EPS = (0.85, 0.80, 0.85)      # eps_hrvg, eps_reg, eps_cond fijos del barrido
T_AMB_DISENO = 283.15         # piso O2: max(283.0, 283.15) = 283.15 K
DH_MAX, DT_MAX = 2.0, 0.5     # umbrales fijos: kJ/kg y K (constraints: no cambiar)
MAX_REAL_CICLOS = 3
EXC = (CicloNoConvergeError, PropertyRangeError, ValueError,
       RuntimeError, NotImplementedError)
SOLVE_KW = {"T_sumidero": T_SUMIDERO, "m_b": M_B, "eta_t": ETA_T, "eta_p": ETA_P,
            "eps_hrvg": EPS[0], "eps_reg": EPS[1], "eps_cond": EPS[2]}
EVAL_KW = {"T_sumidero": T_SUMIDERO, "m_b": M_B,
           "eps_hrvg": EPS[0], "eps_reg": EPS[1], "eps_cond": EPS[2]}
COLS = ("x_b", "P_alta", "T_fuente", "P_star", "s3", "x3", "h3", "T3", "h4",
        "T4", "eta_teqp", "Wnet_teqp", "h4s_teqp", "T4s_teqp", "fase4s", "q4s",
        "h4s_real", "T4s_real", "dh4s", "dT4s", "t_h_real_s", "t_T_real_s",
        "error_real", "rama_fisica", "eta_real", "Wnet_real", "margen_O2_real",
        "clasif_real", "fallas_real", "error_real_ciclo", "error_teqp")


def log(msg): print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)  # noqa: E731


def cargar_kalina():
    """Filas con clasificacion == KALINA: (x_b, P_alta, T_fuente, P_baja=P*)."""
    filas = []
    with open(SRC, "r", newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r.get("clasificacion") != "KALINA":
                continue
            filas.append((float(r["x_b"]), float(r["P_alta"]),
                          float(r["T_fuente"]), float(r["P_baja"])))
    return filas


def paso_teqp(x_b, P_alta, T_fuente, P_star):
    """Ciclo completo con TeqpAdapter en P* + expansion isoentropica de teqp."""
    d = {}
    try:
        b = TeqpAdapter(x=x_b)
        res = resolver_ciclo(b, P_alta=P_alta, P_baja=P_star, T_fuente=T_fuente,
                             x_b=x_b, **SOLVE_KW)
        e3, e4 = res["estados"]["e3"], res["estados"]["e4"]
        s3, x3 = e3.s, e3.x
        h4s, T4s = b.h(P_star, s=s3, x=x3), b.T_from_Ps(P_star, s3, x3)
        fase, q = b.fase_de(P_star, T4s, x3)
        d.update(s3=s3, x3=x3, h3=e3.h, T3=e3.T, h4=e4.h, T4=e4.T,
                 eta_teqp=res["eta"], Wnet_teqp=res["Wnet"], h4s_teqp=h4s,
                 T4s_teqp=T4s, fase4s=fase, q4s=q)
    except EXC as exc:
        d["error_teqp"] = f"{type(exc).__name__}: {exc}"
    return d


def paso_real(x_b, P_star, s3, x3):
    """Pareja h/T_from_Ps con AmmoniaWaterAdapter (mismos s3, x3 de teqp)."""
    d = {"t_h_real_s": "", "t_T_real_s": ""}
    if s3 is None:
        return {**d, "error_real": "sin estado 3 de teqp (ciclo teqp no resuelto)"}
    b, err = AmmoniaWaterAdapter(x=x_b), ""
    for campo, fn, key_t in (("h4s_real", lambda: b.h(P_star, s=s3, x=x3), "t_h_real_s"),
                             ("T4s_real", lambda: b.T_from_Ps(P_star, s3, x3), "t_T_real_s")):
        t0 = time.perf_counter()
        try:
            d[campo] = round(float(fn()), 6)
        except EXC as exc:
            err = (err + " | " if err else "") + f"{campo}: {type(exc).__name__}: {exc}"
        d[key_t] = round(time.perf_counter() - t0, 2)
    d["error_real"] = err
    return d


def paso_real_ciclo(x_b, P_alta, T_fuente, P_star):
    """Ciclo completo con el motor real en P*: eta, Wnet, margen O2, clasificacion."""
    d = {}
    try:
        b = AmmoniaWaterAdapter(x=x_b)
        res = resolver_ciclo(b, P_alta=P_alta, P_baja=P_star, T_fuente=T_fuente,
                             x_b=x_b, **SOLVE_KW)
        T9_amb = condensador.resolver(res["estados"]["e8"], b, T_sumidero=T_AMB_DISENO,
                                      eps=EPS[2], m=M_B)[0].T
        T_bur = b.bubble_point(P_star, x_b)
        val = evaluar_ciclo(b, res, P_alta=P_alta, P_baja=P_star, T_fuente=T_fuente,
                            x_b=x_b, T_amb_diseno=T_AMB_DISENO, **EVAL_KW)
        d.update(eta_real=round(res["eta"], 6), Wnet_real=round(res["Wnet"], 4),
                 margen_O2_real=round(T_bur - T9_amb, 6),
                 clasif_real=val.clasificacion.value,
                 fallas_real=",".join(x.codigo for x in val.fallas))
    except EXC as exc:
        d["error_real_ciclo"] = f"{type(exc).__name__}: {exc}"
    return d


def generar_reporte(filas, no_fisicos):
    r = lambda f, k: f"{f[k]:.6f}" if f.get(k) not in ("", None) else "-"  # noqa: E731
    def T(head, rows):
        return ("| " + " | ".join(head) + " |\n" + "|" + "---|" * len(head) + "\n"
                + ("\n".join("| " + " | ".join(x) + " |" for x in rows) if rows else "—"))
    def clave(f): return (f["x_b"], f["P_alta"], f["T_fuente"])
    filas_t = [(f"{f['x_b']:g}", f"{f['P_alta']:g}", f"{f['T_fuente']:g}",
                r(f, "P_star"), r(f, "eta_teqp"), r(f, "h4s_teqp"), r(f, "h4s_real"),
                r(f, "dh4s"), r(f, "T4s_teqp"), r(f, "T4s_real"), r(f, "dT4s"),
                str(f["rama_fisica"])) for f in filas]
    fisicos = sorted((f for f in filas if f["rama_fisica"] is True),
                     key=lambda f: -f["eta_teqp"])
    no_ev = [f for f in filas if f["rama_fisica"] == "no evaluable"]
    nf = [f for f in filas if f["rama_fisica"] is False]
    t5 = [(f"{f['x_b']:g}", f"{f['P_alta']:g}", f"{f['T_fuente']:g}", r(f, "P_star"),
           r(f, "T4s_teqp"), f.get("fase4s") or "-", r(f, "q4s")) for f in filas]
    t4 = [(f"{f['x_b']}", f"{f['P_alta']:g}", f"{f['T_fuente']:g}",
           r(f, "P_star"), r(f, "eta_teqp")) for f in fisicos]
    mis = ["- x_b={}, P_alta={:g}, T_fuente={:g}, P*={:.6f}".format(
        f["x_b"], f["P_alta"], f["T_fuente"], f["P_star"]) for f in nf]
    nof3 = [(f"  - {clave(f)}: ciclo real no corrio — {f['error_real_ciclo']}"
             if f.get("error_real_ciclo") else
             f"  - {clave(f)}: eta teqp={r(f, 'eta_teqp')} vs real={r(f, 'eta_real')}; "
             f"Wnet teqp={r(f, 'Wnet_teqp')} vs real={r(f, 'Wnet_real')} kW; "
             f"margen O2 real={r(f, 'margen_O2_real')} K; clasif real="
             f"{f.get('clasif_real') or '-'} ({f.get('fallas_real') or 'sin fallas'})")
            for f in nf]
    secciones = [
        "# Reporte — Rama fisica de la expansion isoentropica de turbina — 22 KALINA",
        ("Fecha: 2026-09-24 · TeqpAdapter (calculo) + AmmoniaWaterAdapter (motor "
         "real, IAPWS G4-01) · Tarea 2026-09-24-rama-fisica-22-kalina. Parametros "
         "fijos del barrido: eps 0.85/0.80/0.85, T_sumidero=283.0 K, eta_t=eta_p="
         "0.80, m_b=1.0 kg/s. Expansion como turbina.py:35. Umbrales fijos: "
         f"|dh4s| <= {DH_MAX} kJ/kg y |dT4s| <= {DT_MAX} K."),
        "## 1. Los 22 puntos",
        T(("x_b", "P_alta", "T_fuente", "P*", "eta_teqp", "h4s_teqp", "h4s_real",
           "dh4s", "T4s_teqp", "T4s_real", "dT4s", "rama_fisica"), filas_t),
        "## 2. Conteo y lista de los no fisicos",
        f"- **{len(fisicos)} de {len(filas)} en la rama fisica** (|dh4s| <= "
        f"{DH_MAX} kJ/kg y |dT4s| <= {DT_MAX} K contra el motor real).",
        f"- No fisicos ({len(nf)}):\n" + ("\n".join(mis) if mis else "  - ninguno"),
        f"- No evaluables ({len(no_ev)}):\n" + (
            "\n".join(f"  - {clave(f)}: {f.get('error_teqp') or f.get('error_real')}"
                      for f in no_ev) if no_ev else "  - ninguno"),
        "## 3. No fisicos: ciclo completo con el motor real",
        ("\n".join(nof3) if nf and len(nf) <= MAX_REAL_CICLOS else
         ("Mas de " + str(MAX_REAL_CICLOS) +
          " puntos no fisicos: no se corrio el ciclo real (se listan en la "
          "seccion 2)." if nf else "No habia puntos no fisicos.")),
        "## 4. KALINA confirmados en rama fisica, ordenados por eta",
        T(("x_b", "P_alta", "T_fuente", "P*", "eta_teqp"), t4),
        "## 5. Fase que reporta teqp en (P*, T4s_teqp, x3)",
        T(("x_b", "P_alta", "T_fuente", "P*", "T4s_teqp", "fase", "q"), t5),
        "## 6. Entregables",
        "- scripts/rama_fisica_22_kalina.py; resultados/2026-09-24_rama_22/"
        "rama_fisica_22.csv, REPORTE_RAMA_22.md y run.log.",
    ]
    REPORTE.write_text("\n\n".join(secciones) + "\n", encoding="utf-8")


def principal():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    puntos = cargar_kalina()
    log(f"Puntos KALINA a verificar: {len(puntos)}")
    t0 = time.time()
    filas, no_fisicos = [], []
    for i, (x_b, P_alta, T_fuente, P_star) in enumerate(puntos, 1):
        fila = dict.fromkeys(COLS, "")
        fila.update(x_b=x_b, P_alta=P_alta, T_fuente=T_fuente,
                    P_star=round(P_star, 6))
        d1 = paso_teqp(x_b, P_alta, T_fuente, P_star)
        for k in ("s3", "x3", "h3", "T3", "h4", "T4", "eta_teqp", "Wnet_teqp",
                  "h4s_teqp", "T4s_teqp", "fase4s", "q4s"):
            if k in d1:
                fila[k] = round(d1[k], 6) if isinstance(d1[k], float) else d1[k]
        d2 = paso_real(x_b, P_star, d1.get("s3"), d1.get("x3"))
        fila.update(d2)
        if d1.get("error_teqp"):
            fila["error_teqp"] = d1["error_teqp"]
            fila["rama_fisica"] = "no evaluable"
        elif d2["error_real"]:
            fila["rama_fisica"] = "no evaluable"
        else:
            dh, dT = d1["h4s_teqp"] - d2["h4s_real"], d1["T4s_teqp"] - d2["T4s_real"]
            fila.update(dh4s=round(dh, 6), dT4s=round(dT, 6),
                        rama_fisica=abs(dh) <= DH_MAX and abs(dT) <= DT_MAX)
        filas.append(fila)
        if fila["rama_fisica"] is False:
            no_fisicos.append((x_b, P_alta, T_fuente, P_star))
        log(f"[{time.time() - t0:6.0f}s] {i}/{len(puntos)} x_b={x_b} "
            f"P_alta={P_alta:.0f} T_fuente={T_fuente:.0f} P*={P_star:.6f} "
            f"eta={fila['eta_teqp']} h4s_t={fila['h4s_teqp']} h4s_r={fila['h4s_real']} "
            f"dh4s={fila['dh4s']} dT4s={fila['dT4s']} fase={fila['fase4s']} "
            f"rama={fila['rama_fisica']} {fila['error_real'][:50]}")
    if no_fisicos and len(no_fisicos) <= MAX_REAL_CICLOS:
        log(f"Motor real (ciclo completo) para {len(no_fisicos)} punto(s) "
            f"no fisico(s) en P*")
        for x_b, P_alta, T_fuente, P_star in no_fisicos:
            fila = next(f for f in filas if (f["x_b"], f["P_alta"],
                                             f["T_fuente"]) == (x_b, P_alta, T_fuente))
            fila.update(paso_real_ciclo(x_b, P_alta, T_fuente, P_star))
            log(f"  real x_b={x_b} P_alta={P_alta:.0f} T_fuente={T_fuente:.0f} "
                f"eta={fila['eta_real']} clasif={fila['clasif_real']} "
                f"margen={fila['margen_O2_real']} {fila['error_real_ciclo'][:90]}")
    elif len(no_fisicos) > MAX_REAL_CICLOS:
        log(f"Mas de {MAX_REAL_CICLOS} puntos no fisicos ({len(no_fisicos)}): "
            f"no se corren ciclos con motor real; se listan en el reporte.")
    with open(OUT, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS)
        w.writeheader()
        w.writerows(filas)
    generar_reporte(filas, no_fisicos)
    n_f = sum(1 for f in filas if f["rama_fisica"] is True)
    log(f"Completo en {time.time() - t0:.0f}s; {n_f}/{len(filas)} en rama fisica; "
        f"CSV: {OUT}\nReporte: {REPORTE}")


if __name__ == "__main__":
    principal()