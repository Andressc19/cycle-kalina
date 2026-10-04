"""Re-ejecuta TODAS las filas `NO_CONVERGIO` de los barridos historicos con el bracket
tolerante (MA), una a una (tarea `2026-10-02-reejecutar-no-convergio`: no toca `src/`,
`tests/` ni CSV existentes; salida solo en `resultados/2026-10-02_reejecucion/`). Las 11
variables de `resolver_ciclo` salen de las columnas del CSV y, si faltan, de la constante
homonima del script generador (una indireccion por `from modulo import CONST`) o de la 4a
columna de `UNIVERSO`, donde la procedencia esta comentada; lo no reconstruible sale como
`PARAMETROS_NO_RECONSTRUIBLES`, nunca inventado, y los `rondaN_diagnostico` son companions de
`busqueda_libre_v2.csv` (`CLAVE_JOIN`). Solver: `resolver_ciclo(..., bracket_tolerante=True,
presupuesto_s=300)` con `TeqpVerificado()` (x=0.5, el default de los barridos) y `evaluar_ciclo`
en el MISMO try; si KALINA, `verificar_turbina` con una `AmmoniaWaterAdapter` por worker. 6
workers, CSV incremental y reanudable con una linea por fila en `progreso.log`, tope global de
6 h de reloj; ninguna excepcion aborta y se registra `pid` + orden de fila en el worker (el resultado puede depender del estado previo del proceso: nota del director). Cruce O5 y motor real: `verificar_recuperadas_real.py`.
"""
from __future__ import annotations

import csv, os, re, sys, time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
from src.cycle_solver import resolver_ciclo                             # noqa: E402
from src.properties.ammonia_water_adapter import AmmoniaWaterAdapter   # noqa: E402
from src.properties.teqp_verificado import TeqpVerificado               # noqa: E402
from src.restricciones import evaluar_ciclo                              # noqa: E402
from src.verificacion_motor_real import verificar_turbina                # noqa: E402

RES, OUT = RAIZ / "resultados", RAIZ / "resultados" / "2026-10-02_reejecucion"
CSV_OUT, LOG = OUT / "reejecucion_filas.csv", OUT / "progreso.log"
COLS11 = ("P_alta", "P_baja", "T_fuente", "T_sumidero", "x_b", "m_b", "eta_t", "eta_p", "eps_hrvg", "eps_reg", "eps_cond")
COMP_COLS = ("T_fuente", "T_sumidero", "m_b")          # los que faltan en los companions
EPS_PARTIDA, PRESUP, NW, LIMITE_H = (0.85, 0.75, 0.80), 300.0, 6, 6.0
CAL, F2, F3 = ("scripts/calibracion_elsayed_malla.py", "barridos_2026-09-19/fase2_libre", "barridos_2026-09-19/fase3_real")
S1, S2, S3 = ("scripts/barridos_2026-09-19/fase1_profesor", f"scripts/{F2}", f"scripts/{F3}")
UNIVERSO = (  # csv | T_amb_diseno | script generador [+ CAL] | constantes ausentes del CSV
    "2026-09-22_literatura_kcs11/barrido_literatura_kcs11.csv|303.55|barrido_literatura_kcs11.py+CAL|eta_t=0.80,eta_p=0.80,m_b=1.0",
    "2026-09-24_margen2k/barrido_margen2k.csv|283.15|barrido_margen2k.py+CAL|eps_hrvg=0.85,eps_reg=0.80,eps_cond=0.85",
    "2026-09-23_pinch6_realista/barrido_pinch6_realista.csv|283.15|barrido_pinch6_realista.py+CAL|eta_t=0.80,eta_p=0.80,m_b=1.0",
    "2026-09-23_eps_fijos_085/barrido_eps_fijos_085.csv|283.15|barrido_eps_fijos_085.py+CAL|",
    "2026-09-22_tfuente_bajo/exploracion_tfuente_bajo.csv|283.15|exploracion_tfuente_bajo.py+CAL|eta_t=0.80,eta_p=0.80,m_b=1.0",
    "2026-09-22_frontera_tfuente/frontera_tfuente_teqp.csv|283.15|frontera_tfuente_teqp.py+CAL|eta_t=0.80,eta_p=0.80",
    "2026-09-21_xb_industria/barrido_xb_industria.csv|303.55|resultados/2026-09-21_xb_industria/barrido_xb_industria.py|T_fuente=470.0,T_sumidero=300.032917,m_b=1.0,eta_t=0.85,eta_p=0.75,eps_hrvg=0.85,eps_reg=0.75,eps_cond=0.80",
    f"{F3}/busqueda_husavik.csv|303.55|{S3}/busqueda_base_husavik.py|",
    f"{F3}/busqueda_husavik_v2.csv|283.15|{S3}/busqueda_husavik_v2.py|",
    *(f"{F3}/sensibilidad_{c}.csv|283.15|{S3}/sensibilidad_fase3_ofat.py|" for c in ("P_baja", "eps_cond", "eps_reg", "eta_t", "x_b", "palta", "pbaja", "xb")),
    f"{F3}/mapa_2d_pbaja_epsreg.csv|283.15|{S3}/sensibilidad_fase3_2d.py|",
    *(f"barridos_2026-09-19/fase1_profesor/eta_vs_{c}_profesor.csv|303.55|{S1}/correr_fase1_profesor.py|" for c in ("Palta", "Tambiente", "xb")),
    f"{F2}/busqueda_libre.csv|303.55|{S2}/01_punto_default_y_scan.py|",
    f"{F2}/busqueda_libre_v2.csv|303.55|{S2}/busqueda_libre_v2.py|",
    f"{F2}/prescan_eps_hrvg.csv|303.55|{S2}/prescan_eps_hrvg.py|",
    *(f"{F2}/sensibilidad_{c}.csv|303.55|{S2}/ofat_sensibilidad.py|" for c in ("P_baja", "eps_cond", "eps_hrvg", "eta_t", "x_b")),
    f"{F2}/mapa_2d_pbaja_epscond.csv|303.55|{S2}/malla_2d_sensibilidad.py|P_alta=3000.0,T_fuente=470.0,T_sumidero=300.032917,m_b=1.0,x_b=0.40,eta_t=0.85,eta_p=0.75,eps_hrvg=0.85,eps_reg=0.75",
    f"{F2}/ronda5_diagnostico.csv|303.55|{S2}/ronda5_columnas.py|",
    f"{F2}/ronda6_diagnostico.csv|303.55|{S2}/ronda6_columnas.py|",
    "barridos_2026-09-19/b0_scan_cementera.csv|303.55|b0_scan_cementera.py|T_fuente=583.15,T_sumidero=300.032917,m_b=1.0")
COMPANION = (f"{F2}/ronda5_diagnostico.csv", f"{F2}/ronda6_diagnostico.csv")
CLAVE_JOIN = ("P_alta", "x_b", "eta_t", "eta_p", "eps_hrvg", "eps_reg", "eps_cond", "P_baja")
COLS = ("clave", "n_orden", "orden_worker", "pid", "csv_origenes", "n_origenes", *COLS11, "T_amb_diseno", "eps_supuesta",
        "params_from", "mensaje_original", "convergio", "clasificacion", "eta", "Wnet", "T1", "nF", "repliegues_lo",
        "repliegues_hi", "t_s", "causa", "msg", "fallas", "B_verificado", "B_dh4s", "B_t_s", "B_error", "A_recurrencias",
        "A_verificacion_incompleta", "o5_veredicto")
CAUSA = {"presupuesto de tiempo agotado": "presupuesto agotado", "sin dos extremos evaluables": "sin extremos evaluables",
         "sin cambio de signo": "sin cambio de signo", "punto interior no evaluable": "punto interior no evaluable"}
MOTOR_REAL, _ORDEN = AmmoniaWaterAdapter(x=0.5), {}  # con spawn: 1 motor y 1 contador por worker

def _log(msg: str) -> None:
    LOG.open("a", encoding="utf-8").write(f"{time.strftime('%H:%M:%S')} {msg}\n")

def _num(v):
    try:
        f = float(str(v).strip())
    except (TypeError, ValueError):
        return None
    return f if f - f == 0 else None                # descarta NaN e infinitos

def _const(rel: str, nombre: str, salto: int = 0):
    """Constante de nivel de modulo; un salto mas si hace `from modulo import CONST`."""
    p = RAIZ / rel if rel else None
    if p is None or not p.exists():
        return None
    src = re.sub(r"#[^\n]*", "", p.read_text(encoding="utf-8"))
    if m := re.search(rf"^{nombre}\s*=\s*(-?[\d.]+)\s*$", src, re.M):
        return float(m.group(1))
    imps = re.findall(r"^from\s+(\w+)\s+import\s*(\([^)]*\)|[^\n(]*)", src, re.M | re.S)
    return next((_const(f"scripts/{mod}.py", nombre, salto + 1) for mod, names in imps
                 if salto < 2 and re.search(rf"\b{nombre}\b", names)), None)

def _param(sp: tuple, fila: dict, campo: str, extra: dict, fuente: list):
    """Una de las 11 variables: columna del CSV > constante del script > `extra`."""
    if (v := _num(fila.get(campo))) is not None:
        fuente.append(f"csv:{campo}")
        return v
    for rel in sp:
        if (v := _const(rel, campo.upper())) is not None:
            fuente.append(f"{Path(rel).name}:{campo.upper()}")
            return v
    if campo in extra:
        fuente.append(f"extra:{campo}")
        return float(extra[campo])
    return None

def recolectar() -> list:
    """NO_CONVERGIO del universo, deduplicado por las 11 variables + T_amb_diseno; conserva
    la lista de CSV de origen y deja suelta cada fila no reconstruible."""
    madre = {}
    with (RES / f"{F2}/busqueda_libre_v2.csv").open(encoding="utf-8-sig", newline="") as fh:
        for r in csv.DictReader(fh):
            if all(k := tuple(_num(r.get(c)) for c in CLAVE_JOIN)):
                madre[k] = tuple(_num(r[c]) for c in COMP_COLS)
    datos, sueltas = {}, []
    for linea in UNIVERSO:
        rel, tamb, scripts, extras = linea.split("|")
        tamb, sp, extra = float(tamb), tuple(s if "/" in s else f"scripts/{s}" for s in scripts.split("+")), dict(p.split("=") for p in extras.split(",") if p)
        with (RES / rel).open(encoding="utf-8-sig", newline="") as fh:
            crudos = list(csv.DictReader(fh))
        for n, r in enumerate(crudos, start=2):
            if (r.get("clasificacion") or "").strip() != "NO_CONVERGIO":
                continue
            fuente = []
            d = {c: _param(sp, r, c, extra, fuente) for c in COLS11}
            if rel in COMPANION:                    # completar con el barrido madre
                for c, v in zip(COMP_COLS, madre.get(tuple(_num(r.get(k)) for k in CLAVE_JOIN)) or ()):
                    if d[c] is None and v is not None:
                        d[c], _ = v, fuente.append(f"busqueda_libre_v2.csv:join:{c}")
            if any(d[c] is None for c in COLS11[8:]):    # solo si ni CSV ni script ni extra las dan
                d.update({c: e for c, e in zip(COLS11[8:], EPS_PARTIDA) if d[c] is None})
                fuente.append("EPS_PARTIDA")
            if falta := [c for c in COLS11 if d[c] is None]:
                sueltas.append(dict(clave=f"nopar|{rel}|{n}", csv_origenes=rel, n_origenes=1, T_amb_diseno=tamb, convergio="",
                        params_from="; ".join(fuente), causa="PARAMETROS_NO_RECONSTRUIBLES", msg=f"sin {falta}"))
                continue
            d["clave"] = "|".join(f"{d[c]:.6g}" for c in COLS11) + f"|{tamb:.6g}"
            if (dup := datos.get(d["clave"])) is not None:   # duplicado: acumula sus CSV
                dup.update(csv_origenes=dup["csv_origenes"] + f";{rel}", n_origenes=dup["n_origenes"] + 1)
                continue
            datos[d["clave"]] = dict(d, n_orden=0, csv_origenes=rel, n_origenes=1, T_amb_diseno=tamb,
                eps_supuesta="EPS_PARTIDA" in fuente, params_from="; ".join(fuente), mensaje_original=
                next((str(r.get(c) or "") for c in ("mensaje", "detalle_error", "fallas")
                      if str(r.get(c) or "").strip()), "")[:200])
    return list(datos.values()) + sueltas

def reejecutar(item: dict) -> dict:
    """Una fila con MA. Nunca lanza: el fallo real va a `causa`/`msg`."""
    pid = os.getpid()
    _ORDEN[pid] = _ORDEN.get(pid, 0) + 1
    d = dict(item, pid=pid, orden_worker=_ORDEN[pid])
    if item.get("causa"):                          # PARAMETROS_NO_RECONSTRUIBLES: no se ejecuta
        return d
    kw = {c: item[c] for c in COLS11}
    vk = {**{c: item[c] for c in COLS11 if c not in ("eta_t", "eta_p")}, "T_amb_diseno": item["T_amb_diseno"]}
    real, t0 = TeqpVerificado(x=kw["x_b"]), time.perf_counter()   # regla A+B
    try:
        res = resolver_ciclo(real, bracket_tolerante=True, presupuesto_s=PRESUP, **kw)
        val = evaluar_ciclo(real, res, **vk)                          # en el MISMO try
        bk, fl = res["bracket"], ",".join(f.codigo for f in val.fallas)
        d.update(convergio=True, clasificacion=val.clasificacion.value, causa="", eta=round(res["eta"], 6),
                 Wnet=round(res["Wnet"], 4), nF=bk["nF"], T1=round(res["estados"]["e1"].T, 4),
                 repliegues_lo=bk["repliegues_lo"], repliegues_hi=bk["repliegues_hi"],
                 msg=val.mensaje_reporte()[:200], fallas=fl, A_recurrencias=real.n_recurrencias,
                 A_verificacion_incompleta=real.verificacion_incompleta)
        if val.clasificacion.value == "KALINA":
            b = verificar_turbina(res, P_baja=kw["P_baja"], motor_real=MOTOR_REAL, eta_t=kw["eta_t"])
            d.update(B_verificado=b["verificado"], B_t_s=round(b["t_real_s"], 2), B_error=b["error"][:150],
                     B_dh4s=None if b["dh4s"] is None else round(b["dh4s"], 4))
    except Exception as exc:                                          # nunca aborta la corrida
        msg = f"{type(exc).__name__}: {exc}"[:240]
        d.update(convergio=False, clasificacion="NO_CONVERGIO", msg=msg, causa=next((v for k, v in CAUSA.items() if k in msg), "otro"))
    d["t_s"] = round(time.perf_counter() - t0, 1)
    return d

def main(argv: list) -> int:
    """`--humo N`: las N primeras pendientes, en UN worker real (y al mismo CSV, reanudable)."""
    OUT.mkdir(parents=True, exist_ok=True)
    filas = [dict(d, n_orden=n) for n, d in enumerate(recolectar(), 1)]
    with (CSV_OUT.open(encoding="utf-8-sig", newline="") if CSV_OUT.exists() else open(os.devnull, encoding="utf-8")) as fh:
        hecho = {f["clave"] for f in csv.DictReader(fh)}     # reanudable: no se repite lo ya hecho
    pend, nw = [d for d in filas if d["clave"] not in hecho], NW
    nw, pend = (1, pend[:int(argv[argv.index("--humo") + 1])]) if "--humo" in argv else (nw, pend)
    _log(f"=== inicio {time.strftime('%Y-%m-%d %H:%M:%S')} universo={len(filas)} ya_hechas={len(hecho)} pendientes={len(pend)} workers={nw}")
    t0, nuevo = time.perf_counter(), not CSV_OUT.exists() or CSV_OUT.stat().st_size == 0
    with CSV_OUT.open("a", encoding="utf-8-sig" if nuevo else "utf-8", newline="") as fh:  # BOM solo al crear
        w = csv.DictWriter(fh, fieldnames=COLS, restval="", extrasaction="ignore")
        w.writeheader() if nuevo else None
        pool = ProcessPoolExecutor(max_workers=nw)     # cola continua: ningun worker espera a la tanda
        for n, fut in enumerate(as_completed([pool.submit(reejecutar, d) for d in pend]), 1):
            d, dt = fut.result(), time.perf_counter() - t0
            w.writerow(d)
            fh.flush()
            _log(f"{n}/{len(pend)} ({dt:.0f}s) {d['csv_origenes']} fila={d['n_orden']}:{d['clave']} ->"
                 f" {d.get('clasificacion') or d.get('causa')} pid={d.get('pid')} ord={d.get('orden_worker')} t={d.get('t_s')}s")
            if dt > LIMITE_H * 3600:                   # parada ordenada; lo no empezado se cancela
                _log(f"PARADA ORDENADA: {dt/3600:.2f} h > {LIMITE_H} h; CSV valido y reanudable; {n} de {len(pend)} hechas.")
                break
        pool.shutdown(wait=True, cancel_futures=True)
    _log(f"=== fin {time.perf_counter()-t0:.0f} s")
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))