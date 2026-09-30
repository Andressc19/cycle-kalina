"""Verificacion de 3 KALINA del barrido margen2k con el motor real AmmoniaWaterAdapter
vs TeqpAdapter — tarea 2026-09-24-verificacion-motor-real-y-salto-solver, Parte A.

Se lee el P_baja EXACTO de resultados/2026-09-24_margen2k/barrido_margen2k.csv (NO se
re-optimiza) para los 3 puntos: (0.65,5000,423), (0.80,5000,394), (0.80,4000,394).
Para cada punto y cada motor (TeqpAdapter y AmmoniaWaterAdapter) con los mismos parametros
fijos (eps 0.85/0.80/0.85, T_sumidero=283, eta_t=eta_p=0.80, m_b=1):
  - resolver_ciclo con ese P_baja;
  - margen O2: T9_amb = condensador.resolver(e8, T_sumidero=283.15, eps=0.85, m=1).T,
    T_bur = backend.bubble_point(P_baja, x_b), margen = T_bur - T9_amb;
  - evaluar_ciclo(..., T_amb_diseno=283.15);
  - registro de eta, Wnet, Qi, T1..T10, x3, x5, m3, T9_amb, T_bur, margen,
    clasificacion, fallas, tiempo de computo y error real si algo falla.

Cada corrida del motor real corre en un SUBPROCESO propio (con timeout) para que una
falla o un colgado no tumbe las demas; TeqpAdapter corre en el mismo proceso con
try/except. Reanudable por CSV. No modifica archivos existentes.
"""
from __future__ import annotations
import csv, json, subprocess, sys, time
from pathlib import Path
REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO)); sys.path.insert(0, str(REPO / "scripts"))
from calibracion_elsayed_malla import ETA_P, ETA_T, M_B, T_SUMIDERO  # noqa: E402

OUT_DIR = REPO / "resultados" / "2026-09-24_verificacion"
MARGEN_CSV = REPO / "resultados" / "2026-09-24_margen2k" / "barrido_margen2k.csv"
CSV_PATH = OUT_DIR / "verificacion_motor_real.csv"
REPO_MD = OUT_DIR / "REPORTE_VERIFICACION.md"
PUNTOS = ((0.65, 5000.0, 423.0), (0.80, 5000.0, 394.0), (0.80, 4000.0, 394.0))
EPS = (0.85, 0.80, 0.85)                                # eps_hrvg, eps_reg, eps_cond FIJOS
T_AMB_DISENO = 283.15                                   # piso del criterio O2 (margen2k)
TIMEOUT_REAL = 3300                                     # s; motor real ~8-15 min por ciclo
COLS = ("motor", "x_b", "P_alta", "T_fuente", "P_baja", "eta", "Wnet", "Qi",
        "T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8", "T9", "T10",
        "x3", "x5", "m3", "T9_amb", "T_bur", "margen", "clasificacion",
        "fallas", "tiempo_s", "error")
log = lambda m: print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)  # noqa: E731

def leer_P_baja():
    """P_baja exacto de los 3 puntos desde barrido_margen2k.csv."""
    out = {}
    for f in csv.DictReader(open(MARGEN_CSV, encoding="utf-8")):
        k = (float(f["x_b"]), float(f["P_alta"]), float(f["T_fuente"]))
        if k in PUNTOS and f.get("P_baja"):
            out[k] = float(f["P_baja"])
    faltan = [p for p in PUNTOS if p not in out]
    if faltan:
        raise RuntimeError(f"P_baja no encontrado en {MARGEN_CSV}: {faltan}")
    return out

def ejecutar_job(motor: str, x_b: float, P_alta: float, T_fuente: float,
                 P_baja: float) -> dict:
    from src.components import condensador  # noqa: PLC0415
    from src.cycle_solver import CicloNoConvergeError, resolver_ciclo  # noqa: PLC0415
    from src.properties.adapter import PropertyRangeError  # noqa: PLC0415
    from src.properties.teqp_adapter import TeqpAdapter  # noqa: PLC0415
    from src.restricciones import evaluar_ciclo  # noqa: PLC0415
    if motor == "real":
        from src.properties.ammonia_water_adapter import AmmoniaWaterAdapter  # noqa: PLC0415
    EXC = (CicloNoConvergeError, PropertyRangeError, ValueError,
           RuntimeError, NotImplementedError)
    fila = dict(motor=motor, x_b=x_b, P_alta=P_alta, T_fuente=T_fuente,
                P_baja=round(P_baja, 6), eta="", Wnet="", Qi="", T1="", T2="",
                T3="", T4="", T5="", T6="", T7="", T8="", T9="", T10="",
                x3="", x5="", m3="", T9_amb="", T_bur="", margen="",
                clasificacion="NO_CONVERGIO", fallas="", tiempo_s="", error="")
    t0 = time.perf_counter()
    try:
        backend = (TeqpAdapter(x=x_b) if motor == "teqp" else AmmoniaWaterAdapter(x=x_b))
        res = resolver_ciclo(backend, P_alta=P_alta, P_baja=P_baja,
                             T_fuente=T_fuente, T_sumidero=T_SUMIDERO, x_b=x_b,
                             m_b=M_B, eta_t=ETA_T, eta_p=ETA_P, eps_hrvg=EPS[0],
                             eps_reg=EPS[1], eps_cond=EPS[2])
        e = res["estados"]
        T9_amb = condensador.resolver(e["e8"], backend, T_sumidero=T_AMB_DISENO,
                                      eps=EPS[2], m=M_B)[0].T
        T_bur = backend.bubble_point(P_baja, x_b)
        val = evaluar_ciclo(backend, res, P_alta=P_alta, P_baja=P_baja,
                            T_fuente=T_fuente, T_sumidero=T_SUMIDERO, x_b=x_b,
                            m_b=M_B, eps_hrvg=EPS[0], eps_reg=EPS[1],
                            eps_cond=EPS[2], T_amb_diseno=T_AMB_DISENO)
        fila.update(eta=round(res["eta"], 6), Wnet=round(res["Wnet"], 4),
                    Qi=round(res["Qi"], 4),
                    **{f"T{i}": round(e[f"e{i}"].T, 4) for i in range(1, 11)},
                    x3=round(e["e3"].x, 6), x5=round(e["e5"].x, 6),
                    m3=round(e["e3"].m, 6), T9_amb=round(T9_amb, 6),
                    T_bur=round(T_bur, 6), margen=round(T_bur - T9_amb, 6),
                    clasificacion=val.clasificacion.value,
                    fallas=",".join(x.codigo for x in val.fallas))
    except EXC as exc:
        fila["error"] = f"{type(exc).__name__}: {exc}"
    fila["tiempo_s"] = round(time.perf_counter() - t0, 1)
    return fila

def _cargar():
    done = {}
    if CSV_PATH.exists():
        for f in csv.DictReader(open(CSV_PATH, encoding="utf-8")):
            try:
                done[(f["motor"], float(f["x_b"]), float(f["P_alta"]),
                      float(f["T_fuente"]))] = f
            except (KeyError, ValueError):
                continue
    return done

def _guardar(fila):
    nuevo = not CSV_PATH.exists()
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS)
        nuevo and w.writeheader()
        w.writerow(fila)

def correr_teqp(x_b, P_alta, T_fuente, P_baja):
    fila = ejecutar_job("teqp", x_b, P_alta, T_fuente, P_baja)
    _guardar(fila)
    log(f"teqp   x_b={x_b} P_alta={P_alta:.0f} T_fuente={T_fuente:.0f} "
        f"eta={fila['eta']} clasif={fila['clasificacion']} "
        f"t={fila['tiempo_s']}s {fila['error'][:90]}")
    return fila

def _fila_vacia(motor, x_b, P_alta, T_fuente, P_baja, error):
    return dict(motor=motor, x_b=x_b, P_alta=P_alta, T_fuente=T_fuente,
                P_baja=round(P_baja, 6), eta="", Wnet="", Qi="", T1="", T2="",
                T3="", T4="", T5="", T6="", T7="", T8="", T9="", T10="",
                x3="", x5="", m3="", T9_amb="", T_bur="", margen="",
                clasificacion="NO_CONVERGIO", fallas="", tiempo_s="", error=error)

def correr_real(x_b, P_alta, T_fuente, P_baja):
    cmd = [sys.executable, "-u", str(Path(__file__).resolve()),
           "--job", "real", str(x_b), str(P_alta), str(T_fuente), str(P_baja)]
    fila = None
    try:
        r = subprocess.run(cmd, cwd=str(REPO), capture_output=True, text=True,
                           encoding="utf-8", timeout=TIMEOUT_REAL)
        lineas = [ln for ln in r.stdout.strip().splitlines() if ln.strip()]
        if not lineas:
            fila = _fila_vacia("real", x_b, P_alta, T_fuente, P_baja,
                               f"subprocess sin salida, rc={r.returncode} "
                               f"stderr={r.stderr.strip()[:160]}")
        else:
            fila = json.loads(lineas[-1])
            if r.returncode != 0 and fila.get("error", "") == "":
                fila["error"] = (f"subprocess rc={r.returncode} "
                                 f"stderr={r.stderr.strip()[:160]}")
    except subprocess.TimeoutExpired:
        fila = _fila_vacia("real", x_b, P_alta, T_fuente, P_baja,
                           f"TIMEOUT > {TIMEOUT_REAL}s")
    except Exception as exc:  # noqa: BLE001 - el job real no debe tumbar a los demas
        fila = _fila_vacia("real", x_b, P_alta, T_fuente, P_baja,
                           f"{type(exc).__name__}: {exc}")
    _guardar(fila)
    log(f"real   x_b={x_b} P_alta={P_alta:.0f} T_fuente={T_fuente:.0f} "
        f"eta={fila.get('eta', '')} clasif={fila.get('clasificacion', '')} "
        f"t={fila.get('tiempo_s', '')}s {fila.get('error', '')[:90]}")
    return fila

def generar_reporte(done):
    puntos_resueltos = PUNTOS
    T = lambda hd, filas: ("| " + " | ".join(hd) + " |\n" + "|" + "---|" * len(hd)
                           + "\n" + ("\n".join("| " + " | ".join(f) + " |"
                                               for f in filas) if filas else "—"))  # noqa: E731
    v_ = lambda x: "-" if x in ("", None) else str(x)  # noqa: E731
    filas_t = []
    for k in sorted(done, key=lambda q: (q[2], q[1], q[3])):
        f = done[k]
        filas_t.append((f["motor"], f["x_b"], f["P_alta"], f["T_fuente"],
                        f["P_baja"], v_(f["eta"]), v_(f["Wnet"]), v_(f["margen"]),
                        v_(f["clasificacion"]), v_(f["fallas"]),
                        v_(f["tiempo_s"]), v_(f["error"])))
    pares = []
    for (x_b, P_alta, T_fuente) in puntos_resueltos:
        t, r = (done.get(("teqp", x_b, P_alta, T_fuente)),
                done.get(("real", x_b, P_alta, T_fuente)))
        if t is None or r is None:
            continue
        eta_t, eta_r = (float(t["eta"]) if t.get("eta") else None,
                        float(r["eta"]) if r.get("eta") else None)
        wn_t, wn_r = (float(t["Wnet"]) if t.get("Wnet") else None,
                      float(r["Wnet"]) if r.get("Wnet") else None)
        m_t, m_r = (float(t["margen"]) if t.get("margen") else None,
                    float(r["margen"]) if r.get("margen") else None)
        d = lambda a, b, kind: ("-" if a is None or b is None else
                                (f"{abs(a - b):.6g}" if kind == "abs" else
                                 f"{abs(a - b) / abs(b) * 100:.3g}%"))
        if eta_r is None or r.get("clasificacion") == "NO_CONVERGIO":
            vered = "no evaluable"
        elif t["clasificacion"] == r["clasificacion"]:
            vered = "confirmado"
        else:
            vered = "no confirmado"
        pares.append((f"{x_b}", f"{P_alta:.0f}", f"{T_fuente:.0f}",
                      v_(r["P_baja"]), v_(eta_t), v_(eta_r), d(eta_t, eta_r, "rel"),
                      v_(wn_t), v_(wn_r), d(wn_t, wn_r, "rel"),
                      v_(m_t), v_(m_r), d(m_t, m_r, "rel"),
                      v_(t["clasificacion"]), v_(r["clasificacion"]), vered))
    sec = [
        "## Parte A — Verificacion con AmmoniaWaterAdapter (motor real)",
        "Parametros fijos: eps 0.85/0.80/0.85, T_sumidero=283 K, eta_t=eta_p=0.80, "
        "m_b=1 kg/s; P_baja exacto de barrido_margen2k.csv (sin re-optimizar); margen O2 "
        "con T9_amb a T_sumidero=283.15 K y T_bur=bubble_point(P_baja, x_b); "
        "clasificacion con evaluar_ciclo(T_amb_diseno=283.15).",
        "### A1. Tabla completa por motor y punto",
        T(("motor", "x_b", "P_alta", "T_fuente", "P_baja", "eta", "Wnet",
           "margen_O2", "clasificacion", "fallas", "tiempo_s", "error"), filas_t),
        "### A2. Lado a lado por punto y veredicto",
        T(("x_b", "P_alta", "T_fuente", "P_baja", "eta_teqp", "eta_real",
           "deta_rel", "Wnet_teqp", "Wnet_real", "dWnet_rel", "marg_teqp",
           "marg_real", "dmarg_rel", "clasif_teqp", "clasif_real", "veredicto"),
          pares),
        "Veredictos: **confirmado** = misma clasificacion; **no confirmado** = "
        "clasificacion distinta; **no evaluable** = el motor real no convergio.",
    ]
    md = REPO_MD.read_text(encoding="utf-8")
    md = md.replace("<!-- SECCION_A -->", "\n\n".join(sec) + "\n")
    REPO_MD.write_text(md, encoding="utf-8")

def modo_job(motor, x_b, P_alta, T_fuente, P_baja):
    """Modo hijo: resuelve un solo job y emite su fila como JSON (una linea)."""
    import json as _json  # noqa: PLC0415
    print(_json.dumps(ejecutar_job(motor, float(x_b), float(P_alta),
                                   float(T_fuente), float(P_baja))))

def principal():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    pb = leer_P_baja()
    done = _cargar()
    t0 = time.time()
    for (x_b, P_alta, T_fuente) in PUNTOS:
        P_baja = pb[(x_b, P_alta, T_fuente)]
        if ("teqp", x_b, P_alta, T_fuente) not in done:
            correr_teqp(x_b, P_alta, T_fuente, P_baja)
        if ("real", x_b, P_alta, T_fuente) not in done:
            correr_real(x_b, P_alta, T_fuente, P_baja)
    generar_reporte(_cargar())
    log(f"Parte A completa en {time.time() - t0:.0f}s; CSV: {CSV_PATH}; "
        f"reporte: {REPO_MD}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--job":
        modo_job(*sys.argv[2:])
    else:
        principal()