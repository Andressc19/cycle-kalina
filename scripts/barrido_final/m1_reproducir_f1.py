"""M1 — reproduce los 41 puntos de la Fase 1 del profesor y los compara punto a
punto con la corrida del 2026-09-19 (docs/METODOLOGIA_BARRIDOS_FINAL.md §2, M1).

Pregunta: ¿el código actual, con bracket tolerante MA, protección A+B, marca de
rango y `T_amb_diseno = 300.032917 K`, da la misma clase que la del 2026-09-19?

42 corridas = base con motor `teqp` + base con motor `real` (el que se compara,
porque el 2026-09-19 también usó el motor real) + 9 de `P_alta` + 7 de `x_b` +
24 de `T_sumidero` (las horas de `tamb_profesor.csv`): 41 comparables. Salida en
`resultados/2026-10-06_final_M1/`: los CSV y `REPORTE_M1.md`.
"""

from __future__ import annotations

import csv
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

_DIR = Path(__file__).resolve().parent
_RAIZ = _DIR.parents[1]
for _p in (str(_RAIZ), str(_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import pandas as pd  # noqa: E402

from comun import COLS, PROFESOR, evaluar_punto  # noqa: E402
from src.sensitivity import Barrido, generar_valores  # noqa: E402

OUT = _RAIZ / "resultados" / "2026-10-06_final_M1"
ANT = _RAIZ / "resultados" / "barridos_2026-09-19" / "fase1_profesor"
TAMB = _RAIZ / "scripts" / "barridos_2026-09-19" / "fase1_profesor" / "tamb_profesor.csv"
N_WORKERS = 6
COLS_FILAS = ["grupo", "hora", "valor"] + list(COLS)
CMP_COLS = ["grupo", "valor", "clase_antes", "clase_ahora", "misma_clase",
            "eta_antes", "eta_ahora", "d_eta_pp", "mensaje_antes",
            "mensaje_ahora"]
CLASES = ("KALINA", "CORREGIBLE", "INVIABLE", "NO_CONVERGIO")
ORDEN_GRUPO = ("base", "P_alta", "x_b", "T_amb")
# Punto base anterior: NO_CONVERGIO (CONSTANCIA_PROFESOR.md §2), sin eta.
BASE_ANTES = ("NO_CONVERGIO", None, "")
# Palabra clave ASCII del propio mensaje -> causa legible (no se inventa nada).
CLAVES_MSG = (
    ("fuera de la campana binaria", "el flash L-V no tiene solución: el estado pedido está fuera de la campana bifásica a esa presión"),
    ("fuera de dominio", "el motor no cubre el estado pedido (h fuera de su dominio numérico)"),
    ("presupuesto de tiempo agotado", "MA agotó su presupuesto de 300 s antes de cerrar el lazo exterior"),
    ("punto interior no evaluable", "MA no tiene recuperación para un punto interior de Brent"),
    ("sin dos extremos evaluables", "MA replegó los extremos y no halló dos evaluables en el rango físico"),
    ("sin cambio de signo", "F no cambió de signo en el rango físico de T1"),
    ("T1 degenerado", "T_fuente <= T_sumidero + 2 K: no hay bracket posible"),
    ("lazo interior (frio) no convergio", "el lazo interior de T10 no cerró en max_iter_frio"),
)
_TPL = """# REPORTE M1 — ¿el código actual reproduce la Fase 1 del profesor?

## 1. La pregunta
¿El código actualizado (bracket tolerante MA, protección A+B con `TeqpVerificado`, marca de rango y piso de diseño de O2 en 300.032917 K) da la MISMA clase que la corrida del 2026-09-19 en los 41 puntos de la Fase 1 del profesor?

## 2. Qué se hizo
{nfilas} corridas con `evaluar_punto` (`scripts/barrido_final/comun.py`), todas con `bracket_tolerante=True` y `presupuesto_s=300`, repartidas en {nw} procesos (spawn): el punto base dos veces (motor `teqp` y motor `real`), 9 puntos de `P_alta` (2000–4000 kPa), 7 de `x_b` (0.40–0.70) y las 24 horas de `tamb_profesor.csv` como `T_sumidero`. Son {n} puntos comparables: el punto base aporta el del motor real, porque el 2026-09-19 también usó el motor real.

## 3. Conteo por clase (los {n} puntos comparables)

| Clase | Antes (2026-09-19) | Ahora (2026-10-06) |
|---|---|---|
{tabla}

## 4. Tasa de coincidencia
**{ok}/{n} = {pct:.1f} %** de los puntos conservan su clase.

## 5. Tiempos
- Total de pared de la corrida: {t_pared:.0f} s.
- Por punto (`t_s`): mínimo {tmin:.1f} s, mediana {tmed:.1f} s, máximo {tmax:.1f} s, media {tmean:.1f} s.

## 6. Puntos que cambiaron de clase
{cambiados}

## 7. Nota sobre el piso de O2 y el bracket tolerante
La corrida del 2026-09-19 usó el piso de O2 **por defecto** (303.55 K) y **no** usó MA; esta usa **300.032917 K** y MA. Ese cambio solo puede afectar a puntos que **converjan**: si el punto no converge, O2 y el resto de criterios operativos nunca se evalúan. En los puntos que no convergen, cualquier diferencia de mensaje viene del recorrido del lazo, no del criterio.

## 8. Lo que no se sabe y qué sigue
- No se puede separar el efecto de MA del resto de cambios: la corrida anterior no incluye el contraexperimento sin MA.
- El punto base solo se compara con motor real; la corrida con `teqp` se conserva como dato de recurrencias de la protección A.
- `d_eta_pp` va vacío cuando no hay η en ninguno de los dos lados (ninguno de los dos puntos convergió).
- Siguiente paso: si la coincidencia es {ok}/{n}, M1 cierra y la campaña sigue con M2 (distancia a Kalina desde el punto del profesor).
"""


def construir_tareas() -> list[dict]:
    """Las 42 corridas: base×2 motores + 9 + 7 + 24 barridos del enunciado."""
    tareas = [dict(grupo="base", valor=None, hora=None, motor=mot, tag=f"base_{mot}", combo=dict(PROFESOR)) for mot in ("teqp", "real")]
    for pa in generar_valores(Barrido(2000.0, 4000.0, 250.0)):
        tareas.append(dict(grupo="P_alta", valor=pa, hora=None, motor="teqp", tag=f"P_alta={pa:g}", combo=dict(PROFESOR, P_alta=pa)))
    for xb in generar_valores(Barrido(0.40, 0.70, 0.05)):
        tareas.append(dict(grupo="x_b", valor=xb, hora=None, motor="teqp", tag=f"x_b={xb:g}", combo=dict(PROFESOR, x_b=xb)))
    for _, r in pd.read_csv(TAMB).iterrows():
        tareas.append(dict(grupo="T_amb", valor=float(r["T_amb_K"]), hora=int(r["hora"]), motor="teqp", tag=f"hora={int(r['hora']):02d}", combo=dict(PROFESOR, T_sumidero=float(r["T_amb_K"]))))
    return tareas


def comparables(tareas: list[dict]) -> list[dict]:
    """Las 41 tareas con contraparte el 2026-09-19 (el base solo con motor real)."""
    return [t for t in tareas if t["grupo"] != "base" or t["motor"] == "real"]


def _corrida(tarea: dict) -> dict:
    """Un punto evaluado y aplanado a las columnas de `m1_filas.csv`."""
    fila = evaluar_punto(tarea["combo"], motor=tarea["motor"], tag=tarea["tag"])
    fila.update(grupo=tarea["grupo"], hora=tarea["hora"], valor=tarea["valor"])
    return {c: fila.get(c) for c in COLS_FILAS}


def _reg(r) -> tuple:
    """`(clase, eta, mensaje)` de una fila de los CSV del 2026-09-19."""
    return (str(r["clasificacion"]), None if pd.isna(r["eta"]) else float(r["eta"]), "" if pd.isna(r["mensaje"]) else str(r["mensaje"]))


def _antes() -> dict:
    """`{(grupo, clave): (clase, eta, mensaje)}` del 2026-09-19; la clave es el
    valor de la variable barrida y, para `T_amb`, la `hora`."""
    d = {("base", "base"): BASE_ANTES}
    for grupo, nombre in (("P_alta", "eta_vs_Palta_profesor.csv"), ("x_b", "eta_vs_xb_profesor.csv")):
        for _, r in pd.read_csv(ANT / nombre).iterrows():
            d[(grupo, round(float(r[grupo]), 6))] = _reg(r)
    for _, r in pd.read_csv(ANT / "eta_vs_Tambiente_profesor.csv").iterrows():
        d[("T_amb", int(r["hora"]))] = _reg(r)
    return d


def comparar(filas: list[dict]) -> list[dict]:
    """Compara cada punto con su contraparte y escribe `m1_comparacion.csv`."""
    antes, salida = _antes(), []
    for f in filas:
        if f["grupo"] == "base" and f["motor"] != "real":
            continue
        clave = "base" if f["grupo"] == "base" else int(f["hora"]) if f["grupo"] == "T_amb" else round(float(f["valor"]), 6)
        ca, ea, ma = antes[(f["grupo"], clave)]
        ce, mc = f["eta"], f["mensaje"] or ""
        salida.append(dict(grupo=f["grupo"], valor=f["valor"], clase_antes=ca, clase_ahora=f["clasificacion"], misma_clase=ca == f["clasificacion"], eta_antes=ea, eta_ahora=ce, d_eta_pp=None if (ea is None or ce is None) else (ce - ea) * 100.0, mensaje_antes=ma[:80], mensaje_ahora=mc[:80]))
    with open(OUT / "m1_comparacion.csv", "w", encoding="utf-8", newline="") as fh:
        esc = csv.DictWriter(fh, fieldnames=CMP_COLS)
        esc.writeheader()
        esc.writerows(salida)
    return salida


def _explicar(ahora: str, antes: str) -> str:
    """Causa legible deducida del propio mensaje; o dice que no la hay."""
    for clave, txt in CLAVES_MSG:
        if clave in ahora:
            return f'"{clave}": {txt}' + (" (mismo mecanismo que el 2026-09-19)" if clave in antes else " (mecanismo NUEVO respecto al 2026-09-19)")
    return ("mismo mensaje en las dos corridas: no hay diferencia de mecanismo" if ahora and antes and ahora[:40] == antes[:40] else "SIN EXPLICACIÓN: el mensaje no contiene ninguna causa conocida")


def _conteo(vals) -> dict:
    c: dict = {}
    for v in vals:
        c[v] = c.get(v, 0) + 1
    return c


def reporte(cmp: list[dict], filas: list[dict], t_pared: float) -> str:
    """Escribe `REPORTE_M1.md` en lenguaje llano y devuelve su texto."""
    n, ok = len(cmp), sum(1 for c in cmp if c["misma_clase"])
    antes, ahora = _conteo(c["clase_antes"] for c in cmp), _conteo(c["clase_ahora"] for c in cmp)
    ts = sorted(f["t_s"] for f in filas if f["t_s"])
    cambiados = [c for c in cmp if not c["misma_clase"]]
    tabla_cam = "\n".join(["| Grupo | Valor | Antes | Ahora | Explicación según el mensaje |", "|---|---|---|---|---|"] + [f"| {c['grupo']} | {c['valor']} | {c['clase_antes']} | {c['clase_ahora']} | {_explicar(c['mensaje_ahora'], c['mensaje_antes'])} |" for c in cambiados]) if cambiados else "Ninguno: los 41 puntos conservan su clase."
    txt = _TPL.format(n=n, ok=ok, pct=100.0 * ok / n, nw=N_WORKERS, nfilas=len(filas), cambiados=tabla_cam, t_pared=t_pared, tmin=ts[0], tmed=ts[len(ts) // 2], tmax=ts[-1], tmean=sum(ts) / len(ts), tabla="\n".join(f"| {c} | {antes.get(c, 0)} | {ahora.get(c, 0)} |" for c in CLASES))
    (OUT / "REPORTE_M1.md").write_text(txt, encoding="utf-8")
    return txt


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    tareas = construir_tareas()
    print(f"{len(tareas)} corridas | {N_WORKERS} workers | {len(comparables(tareas))} comparables -> {OUT}", flush=True)
    filas, t0 = [], time.perf_counter()
    with open(OUT / "m1_filas.csv", "w", encoding="utf-8", newline="") as fh:
        esc = csv.DictWriter(fh, fieldnames=COLS_FILAS)
        esc.writeheader()
        fh.flush()
        with ProcessPoolExecutor(max_workers=N_WORKERS) as ex:
            for n, fut in enumerate(as_completed([ex.submit(_corrida, t) for t in tareas]), 1):
                f = fut.result()
                filas.append(f)
                esc.writerow(f)
                fh.flush()
                print(f"[{n}/{len(tareas)}] {f['grupo']} {f['tag']} clase={f['clasificacion']} t={f['t_s']:.1f}s", flush=True)
    t_pared = time.perf_counter() - t0
    filas.sort(key=lambda f: (ORDEN_GRUPO.index(f["grupo"]), str(f["tag"])))
    cmp_ = comparar(filas)
    reporte(cmp_, filas, t_pared)
    ok = sum(1 for c in cmp_ if c["misma_clase"])
    print(f"\nfin: {len(filas)} filas en {t_pared:.0f} s | coincidencia {ok}/{len(cmp_)} con la misma clase | conteo ahora {_conteo(c['clase_ahora'] for c in cmp_)}", flush=True)


if __name__ == "__main__":
    main()