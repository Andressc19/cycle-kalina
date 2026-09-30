"""Barrido 30 puntos pinch 6 K (2026-09-23): x_b {0.60..0.80} x T_fuente
{394, 423} x P_alta {3000, 4000, 5000}. Mismo metodo que
`calibracion_elsayed_malla.py` pero con pinch PARAMETRO (`calibracion_pinch.py`,
6.0 K): con 4 K los eps quedaban muy altos y el margen de O2 era ~4 K por
construccion. Clasificacion con piso realista ya validado (T_amb_diseno
=283.15 K). Solo TeqpAdapter; reanudable por CSV; ningun punto se oculta.
"""
from __future__ import annotations

import csv
import sys
import time
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))

from calibracion_elsayed_malla import M_B, T_SUMIDERO  # noqa: E402
from calibracion_pinch import calibrar_P_baja, calibrar_eps  # noqa: E402
from src._cycle_loops import CicloNoConvergeError  # noqa: E402
from src.properties.adapter import PropertyRangeError  # noqa: E402
from src.properties.teqp_adapter import TeqpAdapter  # noqa: E402
from src.restricciones import Clasificacion, evaluar_ciclo  # noqa: E402

OUT_DIR = REPO / "resultados" / "2026-09-23_pinch6_realista"
CSV_PATH = OUT_DIR / "barrido_pinch6_realista.csv"
REPORTE_PATH = OUT_DIR / "REPORTE_PINCH6_REALISTA.md"
OLD_CSV = REPO / "resultados" / "2026-09-22_o2_tamb_realista" / "reclasificacion_o2.csv"
PINCH = 6.0
XBS = (0.60, 0.65, 0.70, 0.75, 0.80)
P_ALTAS = (3000.0, 4000.0, 5000.0)
T_FUENTES = (394.0, 423.0)
T_AMB_REAL = 283.15
COLS = ("x_b", "P_alta", "T_fuente", "pinch", "P_baja", "eps_hrvg",
        "eps_reg", "eps_cond", "eps_realista", "convergio", "clasificacion",
        "eta", "Wnet", "fallas", "detalle_error")
EXC_CATCH = (CicloNoConvergeError, PropertyRangeError, ValueError,
             RuntimeError, NotImplementedError)
NOCONV = Clasificacion.NO_CONVERGIO.value
CLAVE = lambda f: (float(f["x_b"]), float(f["P_alta"]), float(f["T_fuente"]))  # noqa: E731
CONV = lambda f: str(f.get("convergio")) == "True"  # noqa: E731
REAL = lambda f: str(f.get("eps_realista")) == "True"  # noqa: E731
KAL = lambda f: f.get("clasificacion") == "KALINA"  # noqa: E731
v = lambda x: str(x) if x not in ("", None) else "-"  # noqa: E731


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def resolver_punto(backend, x_b, P_alta, T_fuente) -> dict:
    fila = dict(x_b=x_b, P_alta=P_alta, T_fuente=T_fuente, pinch=PINCH,
                P_baja="", eps_hrvg="", eps_reg="", eps_cond="",
                eps_realista="", convergio=False, clasificacion=NOCONV,
                eta="", Wnet="", fallas="", detalle_error="")
    try:
        P_baja = calibrar_P_baja(backend, x_b, P_alta, PINCH)
    except EXC_CATCH as exc:
        fila["detalle_error"] = f"{type(exc).__name__}: {exc}"
        return fila
    fila["P_baja"] = round(P_baja, 6)
    try:
        cal = calibrar_eps(backend, x_b=x_b, P_alta=P_alta, P_baja=P_baja,
                           T_fuente=T_fuente, pinch=PINCH)
    except EXC_CATCH as exc:
        fila["detalle_error"] = f"{type(exc).__name__}: {exc}"
        return fila
    res = cal["resultado"]
    eps = (cal["eps_hrvg"], cal["eps_reg"], cal["eps_cond"])
    fila.update(eps_hrvg=round(eps[0], 6), eps_reg=round(eps[1], 6),
                eps_cond=round(eps[2], 6),
                eps_realista=str(not any(e > 0.95 for e in eps)))
    kw = dict(P_alta=P_alta, P_baja=P_baja, T_fuente=T_fuente, x_b=x_b,
              m_b=M_B, eps_hrvg=eps[0], eps_reg=eps[1], eps_cond=eps[2])
    try:
        val = evaluar_ciclo(backend, res, T_sumidero=T_SUMIDERO,
                            T_amb_diseno=T_AMB_REAL, **kw)
    except EXC_CATCH as exc:
        fila["detalle_error"] = f"{type(exc).__name__}: {exc}"
        fila["convergio"] = True
        return fila
    fila.update(convergio=True, clasificacion=val.clasificacion.value,
                eta=round(res["eta"], 6), Wnet=round(res["Wnet"], 4),
                fallas=",".join(x.codigo for x in val.fallas))
    return fila


def _cargar(path: Path) -> dict:
    if not path.exists():
        return {}
    d = {}
    with open(path, "r", newline="", encoding="utf-8") as f:
        for fila in csv.DictReader(f):
            try:
                d[CLAVE(fila)] = fila
            except (KeyError, ValueError):
                continue
    return d


def cargar_todas() -> tuple[set, list]:
    d = _cargar(CSV_PATH)
    return set(d), list(d.values())


def escribir_fila(fila: dict, done: set) -> set:
    nuevo = not CSV_PATH.exists()
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        if nuevo:
            w.writeheader()
        w.writerow(fila)
    done.add(CLAVE(fila))
    return done


def generar_reporte(todas: list) -> None:
    n = len(todas)
    conv = [f for f in todas if CONV(f)]
    c_clas = Counter(f["clasificacion"] for f in todas)
    k = [f for f in conv if KAL(f)]
    kr = [f for f in k if REAL(f)]
    k_no = [f for f in k if not REAL(f)]
    errs = sorted({f["detalle_error"][:60] for f in todas if f["detalle_error"]})
    n_sobre95 = sum(1 for f in conv if not REAL(f))
    n_clip = sum(1 for f in conv if any(round(float(f[c]), 6) == 0.999 for c in ("eps_hrvg", "eps_reg", "eps_cond") if f[c]))
    e_max = {c: max((float(f[c]) for f in conv if f[c]), default=float("nan")) for c in ("eps_hrvg", "eps_reg", "eps_cond")}
    n_col95 = {c: sum(1 for f in conv if f[c] and float(f[c]) > 0.95) for c in ("eps_hrvg", "eps_reg", "eps_cond")}
    orden = sorted(kr, key=lambda f: -float(f["eta"]))
    kr_rows = ("| x_b | P_alta | T_fuente | P_baja | eps_hrvg | eps_reg | eps_cond | eta | Wnet [kW] |\n"
               "|---|---|---|---|---|---|---|---|---|\n" + "\n".join(
               f"| {f['x_b']} | {f['P_alta']} | {f['T_fuente']} | {f['P_baja']} | {f['eps_hrvg']} | "
               f"{f['eps_reg']} | {f['eps_cond']} | {f['eta']} | {f['Wnet']} |" for f in orden)
               if orden else "Ninguno.")

    def mejor(grupo):
        for pool, crit in (([f for f in grupo if KAL(f) and REAL(f)], "KALINA + eps_realista"),
                           ([f for f in grupo if KAL(f)], "KALINA (algun eps > 0.95)"),
                           ([f for f in grupo if CONV(f)], "sin KALINA; mejor eta entre convergentes")):
            if pool:
                return sorted(pool, key=lambda f: -float(f["eta"]))[0], crit
        return grupo[0], "ningun punto convergente"
    xb_rows = []
    for x_b in XBS:
        g = [f for f in todas if float(f["x_b"]) == x_b]
        if not g:
            continue
        m, crit = mejor(g)
        xb_rows.append(f"| {x_b:.2f} | {crit} | {v(m['clasificacion'])} | {v(m['eta'])} | "
                       f"{v(m['Wnet'])} | {m['P_alta']}/{m['T_fuente']} |")

    old = _cargar(OLD_CSV)
    comunes = [(o, f) for f in todas if (o := old.get(CLAVE(f)))]
    comp_rows = ("| x_b | P_alta | T_fuente | eta 4K | clasif 4K | eta 6K | clasif 6K |\n"
                 "|---|---|---|---|---|---|---|\n"
                 + "\n".join(f"| {o['x_b']} | {o['P_alta']} | {o['T_fuente']} | {o['eta']} | "
                             f"{o['clasificacion_realista']} | {f.get('eta') or '-'} | "
                             f"{f.get('clasificacion') or '-'} |" for o, f in comunes)
                 if comunes else "Ninguno.")
    o2_4 = sum(1 for o, _ in comunes if "O2" in (o.get("fallas_realista") or "").split(","))
    o2_6 = sum(1 for _, f in comunes if "O2" in (f.get("fallas") or "").split(","))
    e4 = [float(o["eta"]) for o, _ in comunes if o.get("eta")]
    e6 = [float(f["eta"]) for _, f in comunes if f.get("eta")]
    d_eta = (sum(e4) / len(e4) - sum(e6) / len(e6)) * 100 if (e4 and e6) else 0.0
    o2_all = sum(1 for f in conv if "O2" in (f.get("fallas") or "").split(","))
    o1_all = sum(1 for f in conv if "O1" in (f.get("fallas") or "").split(","))

    hal = [
        f"**Eps realistas**: de {len(conv)} convergentes, {len(conv) - n_sobre95} tienen los "
        f"tres eps <= 0.95 y {n_sobre95} tienen alguno > 0.95 (marcados `eps_realista=False`); "
        f"{n_clip} recorte(s) clavados en 0.999. Puntos con eps > 0.95 por columna: "
        f"eps_hrvg={n_col95['eps_hrvg']}, eps_reg={n_col95['eps_reg']}, "
        f"eps_cond={n_col95['eps_cond']}. Maximos: eps_hrvg={e_max['eps_hrvg']:.4f}, "
        f"eps_reg={e_max['eps_reg']:.4f}, eps_cond={e_max['eps_cond']:.4f}.",
        f"**KALINA con eps realistas = {len(kr)} de {n}** (el numero que importa); {len(k)} son "
        f"KALINA en total, de los cuales {len(k_no)} tienen algun eps > 0.95.",
        f"**O2**: {o2_all} punto(s) convergente(s) siguen bloqueados por O2 en esta malla; en "
        f"los {len(comunes)} puntos comunes, pinch 4K bloqueaba O2 en {o2_4} y pinch 6K en {o2_6}.",
        f"**Costo de eta del pinch mayor**: en los {len(comunes)} puntos comunes la eta media "
        f"baja {d_eta:.2f} puntos porcentuales (4K -> 6K).",
        f"**Rango usado**: x_b >= 0.60 (sin fracciones de NH3 bajas); recorte de eps a "
        f"[0.01, 0.999]; solo `TeqpAdapter`.",
    ]
    if o1_all:
        hal.append(f"**O1** (titulo de turbina < 0.90) sigue en {o1_all} punto(s) no-KALINA; "
                   f"el pinch mayor no lo corrige.")
    if errs:
        hal.append("Errores registrados (nunca ocultados): " + "; ".join(errs[:4]) + ".")

    cls = ("KALINA", "VALIDO_ADVERTENCIA", "CORREGIBLE", "DEGENERADO",
           "INVIABLE", "NO_CONVERGIO")
    ct = ("| Clasificacion | Puntos |\n|---|---|\n"
          + "\n".join(f"| {c} | {c_clas.get(c, 0)} |" for c in cls)
          + f"\n| **Total** | **{n}** |\n| **KALINA con eps_realista=True** | **{len(kr)}** |")
    cab = (f"# Reporte — Barrido pinch 6 K realista (30 puntos)\n\n"
           "Fecha: 2026-09-23 · Motor: **solo `TeqpAdapter`** · Tarea "
           "2026-09-23-barrido-pinch6-realista (no toca `src/` ni archivos existentes).\n"
           f"Grid: {len(XBS)} x {len(P_ALTAS)} x {len(T_FUENTES)} = {len(XBS) * len(P_ALTAS) * len(T_FUENTES)} puntos; "
           "`T_sumidero=283.0 K`, `eta_t=eta_p=0.80`, `m_b=1.0 kg/s` (de "
           "`calibracion_elsayed_malla.py`); pinch **6 K** (`calibracion_pinch.py`, mismo "
           "metodo con el pinch como parametro). Clasificacion con `T_amb_diseno=283.15 K` "
           "(piso realista validado, pasado explicitamente).")
    resumen = f"## Resumen ejecutivo\n\n**KALINA: {len(k)} de {n} puntos; con eps realistas " \
              f"(<= 0.95): **{len(kr)}**. Convergen {len(conv)}; los demas estan en el CSV " \
              f"con `detalle_error`."
    metodo = ("## Metodologia y limites\n\n"
              "- `P_baja` = burbuja a (`T_sumidero` + 6 K, x_b), brentq en [50, P_alta-10] kPa; "
              "eps despejados en forma cerrada (T2 = T_fuente - 6, T6 = T10 + 6, "
              "T9 = T_sumidero + 6), recortados a [0.01, 0.999] y re-resolucion. "
              "`eps_realista` es una marca (los tres eps <= 0.95), nunca descarta el punto.\n"
              "- Un resolve por punto; captura de `CicloNoConvergeError`/`PropertyRangeError`/`ValueError`/`RuntimeError`; reanudable por CSV.\n"
              "- Ventana: T_fuente 394 K (≈ Húsavík) y 423 K; P_alta 3000-5000 kPa; x_b 0.60-0.80.")
    entrega = ("## Entregables\n\n"
               "- `barrido_pinch6_realista.csv` — 30 filas: x_b, P_alta, T_fuente, pinch, "
               "P_baja, eps_hrvg, eps_reg, eps_cond, eps_realista, convergio, clasificacion, "
               "eta, Wnet, fallas, detalle_error.\n- `run.log` de la corrida.\n- Este reporte.")
    secciones = [cab, resumen, f"## Conteo por clasificacion\n\n{ct}",
                 f"## KALINA con eps realistas, ordenados por eta\n\n{kr_rows}",
                 f"## Mejor punto por x_b\n\n| x_b | criterio | clasificacion | eta | "
                 "Wnet [kW] | P_alta/T_fuente |\n|---|---|---|---|---|---|\n" + "\n".join(xb_rows),
                 f"## Comparacion pinch 4 K vs pinch 6 K ({len(comunes)} puntos comunes "
                 f"con `reclasificacion_o2.csv`)\n\n{comp_rows}",
                 "## Hallazgos\n\n" + "\n".join(f"{i + 1}. {h}" for i, h in enumerate(hal)),
                 metodo, entrega]
    REPORTE_PATH.write_text("\n\n".join(secciones) + "\n", encoding="utf-8")


def principal() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    done, _ = cargar_todas()
    t0 = time.time()
    for x_b in XBS:
        for T_fuente in T_FUENTES:
            for P_alta in P_ALTAS:
                if (x_b, P_alta, T_fuente) in done:
                    continue
                fila = resolver_punto(TeqpAdapter(x=x_b), x_b, P_alta, T_fuente)
                dt = time.time() - t0
                done = escribir_fila(fila, done)
                log(f"[{dt:6.0f}s] x_b={x_b} P_alta={P_alta:.0f} T_fuente={T_fuente:.0f} "
                    f"clasif={fila['clasificacion']} real={fila['eps_realista'] or '-'} "
                    f"eta={fila['eta']} Wnet={fila['Wnet']} fallas={fila['fallas'] or '-'} "
                    f"{fila['detalle_error'][:70]}")
    generar_reporte(cargar_todas()[1])
    log(f"Malla completa en {time.time()-t0:.0f}s; CSV: {CSV_PATH}\nReporte: {REPORTE_PATH}")


if __name__ == "__main__":
    principal()