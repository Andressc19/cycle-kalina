"""M2 nivel 1 — con UN solo cambio al enunciado del profesor, ¿aparece KALINA? Fase A (malla): cada una de las 10 variables toma 10 valores equiespaciados de su rango, con las otras 10 exactamente como las dio el profesor (100 corridas, 6 procesos). Fase B (bisección): entre cada par de vecinos de la malla donde cambia la convergencia o aparece KALINA se refina la frontera por bisección, en rondas paralelas. Salida en `resultados/2026-10-06_final_M2/`: `m2n1_malla.csv`, `m2n1_biseccion.csv`, `m2n1_fronteras.csv`, `m2n1_resumen.csv` y `REPORTE_M2_N1.md`. Con `M2_HUMO=1` la malla queda en 2 variables x 2 valores, sin bisección, y todo se escribe en `.../humo/`.
"""
from __future__ import annotations

import csv, os, sys, time  # noqa: E401,E402
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

_DIR = Path(__file__).resolve().parent
_RAIZ = _DIR.parents[1]
sys.path[:0] = [str(_RAIZ), str(_DIR)]
import numpy as np  # noqa: E402

from comun import COLS, PROFESOR, evaluar_punto  # noqa: E402

HUMO = os.environ.get("M2_HUMO") == "1"
OUT = _RAIZ / "resultados" / ("2026-10-06_final_M2/humo" if HUMO else "2026-10-06_final_M2")
N_WORKERS = 6
# variable -> (tipo, a, b, tolerancia de bisección): rangos y tolerancias fijados por el director.
RANGOS = {"P_alta": ("diseño", 1000.0, 10000.0, 10.0), "P_baja": ("diseño", 150.0, 1500.0, 10.0),
          "x_b": ("diseño", 0.30, 0.90, 0.005), "eta_t": ("diseño", 0.75, 0.90, 0.005), "eta_p": ("diseño", 0.65, 0.85, 0.005),
          "eps_hrvg": ("diseño", 0.75, 0.85, 0.005), "eps_reg": ("diseño", 0.75, 0.85, 0.005), "eps_cond": ("diseño", 0.75, 0.85, 0.005),
          "T_fuente": ("sitio", 340.0, 623.15, 0.5), "T_sumidero": ("sitio", 283.15, 303.55, 0.5)}
CMALLA = ["fase", "variable", "valor"] + list(COLS)
CBISE = ["fase", "variable", "frontera", "iteracion", "valor"] + list(COLS)
CFRON = ["variable", "tipo", "frontera", "lado_si", "lado_no", "ancho_final", "iteraciones", "clase_lado_si", "D_lado_si", "codigos_falla_lado_si"]
CREST = ["variable", "tipo", "n_converge", "n_kalina", "n_corregible", "n_inviable", "n_no_convergio", "valor_conv_mas_cercano_prof",
         "valor_kalina_mas_cercano_prof", "d_normalizada", "D_minimo", "valor_D_minimo", "criterios_bloqueantes_frecuentes"]


def _cumple(f: dict, frontera: str) -> bool:
    """¿La fila cumple el criterio de esa frontera (convergencia o KALINA)?"""
    return bool(f["convergio"]) if frontera == "convergencia" else f["clasificacion"] == "KALINA"


def _eval(t: dict) -> dict:
    """Corre UN punto (una sola variable cambiada sobre el punto del profesor)."""
    f = evaluar_punto(dict(PROFESOR, **{t["variable"]: t["valor"]}), motor="teqp", tag=f'{t["variable"]}={t["valor"]:g}')
    f.update({k: t.get(k) for k in ("fase", "variable", "valor", "frontera", "iteracion")})
    return f


def _ejecutar(tareas: list, cab: list, fh, esc) -> list:
    """Todo el lote en el pool; devuelve las filas en el orden en que se enviaron."""
    orden = [None] * len(tareas)
    with ProcessPoolExecutor(max_workers=N_WORKERS) as ex:
        futs = {ex.submit(_eval, t): i for i, t in enumerate(tareas)}
        for n, fu in enumerate(as_completed(futs), 1):
            f = fu.result()
            orden[futs[fu]] = f; esc.writerow({c: f.get(c) for c in cab}); fh.flush()
            print(f'[{n}/{len(tareas)}] {f["variable"]}={f["valor"]:g} {f["clasificacion"]} {f["t_s"]:.1f}s', flush=True)
    return orden


def fase_malla(fh, esc) -> list:
    """Fase A: la malla gruesa (10x10; en humo 2x2 con las 2 primeras variables)."""
    vals = {v: np.linspace(r[1], r[2], 2 if HUMO else 10) for v, r in RANGOS.items()}
    if HUMO: vals = dict(list(vals.items())[:2])
    t = [dict(fase="malla", variable=v, valor=float(x)) for v, xs in vals.items() for x in xs]
    return _ejecutar(t, CMALLA, fh, esc)


def detectar(filas: list) -> list:
    """Fronteras entre vecinos de la malla donde cambia convergencia o KALINA."""
    fr = []
    for var, (tipo, _a, _b, tol) in RANGOS.items():
        pts = sorted((f for f in filas if f["variable"] == var), key=lambda f: f["valor"])
        for p, q in zip(pts, pts[1:]):
            for nom in ("convergencia", "KALINA"):
                if _cumple(p, nom) != _cumple(q, nom):
                    fr.append(dict(variable=var, tipo=tipo, frontera=nom, lo=p["valor"], hi=q["valor"], lo_si=_cumple(p, nom), f_lo=p, f_hi=q, tol=tol, iter=0))
    return fr


def fase_biseccion(todos: list, fh, esc) -> list:
    """Fase B: rondas de bisección sobre todas las fronteras; muta `todos`."""
    ronda, activos, hechas = 0, todos, []
    while activos:
        ronda += 1
        for f in activos: print(f'[ronda {ronda}] {f["variable"]} {f["frontera"]} {f["lo"]:g}..{f["hi"]:g}', flush=True)
        t = [dict(fase="biseccion", variable=f["variable"], frontera=f["frontera"], iteracion=f["iter"], valor=(f["lo"] + f["hi"]) / 2) for f in activos]
        medias = _ejecutar(t, CBISE, fh, esc)
        hechas += medias
        vivos = []
        for f, m in zip(activos, medias):
            if _cumple(m, f["frontera"]) == f["lo_si"]: f["lo"], f["f_lo"] = m["valor"], m
            else: f["hi"], f["f_hi"] = m["valor"], m
            f["iter"] += 1
            if f["hi"] - f["lo"] >= f["tol"] and f["iter"] < 10: vivos.append(f)
        activos = vivos
    return hechas


def filas_fronteras(fr: list) -> list:
    """Una fila por frontera: el lado que SÍ cumple, el que no y el ancho final."""
    out = []
    for f in fr:
        si, no = (f["f_lo"], f["f_hi"]) if f["lo_si"] else (f["f_hi"], f["f_lo"])
        out.append(dict(variable=f["variable"], tipo=f["tipo"], frontera=f["frontera"], lado_si=si["valor"], lado_no=no["valor"], ancho_final=f["hi"] - f["lo"], iteraciones=f["iter"], clase_lado_si=si["clasificacion"], D_lado_si=si["D"], codigos_falla_lado_si=si["codigos_falla"]))
    return out


def filas_resumen(filas: list) -> list:
    """Una fila por variable: conteos, valores más cercanos al profesor y bloqueos."""
    out = []
    for var, (tipo, a, b, _t) in RANGOS.items():
        fs = [f for f in filas if f["variable"] == var]
        if not fs: out.append({**dict.fromkeys(CREST), "variable": var, "tipo": tipo}); continue
        conv = [f for f in fs if f["convergio"]]
        kal = [f for f in fs if f["clasificacion"] == "KALINA"]
        c = Counter(f["clasificacion"] for f in fs)
        dmin = min([f for f in fs if f["D"] is not None], key=lambda f: f["D"], default=None)
        cods = Counter(x for f in conv if f["clasificacion"] != "KALINA" for x in (f["codigos_falla"] or "").split(",") if x)
        vm = min(conv, key=lambda f: abs(f["valor"] - PROFESOR[var]))["valor"] if conv else None
        vk = min(kal, key=lambda f: abs(f["valor"] - PROFESOR[var]))["valor"] if kal else None
        out.append(dict(variable=var, tipo=tipo, n_converge=len(conv), n_kalina=len(kal), n_corregible=c["CORREGIBLE"], n_inviable=c["INVIABLE"], n_no_convergio=c["NO_CONVERGIO"], valor_conv_mas_cercano_prof=vm, valor_kalina_mas_cercano_prof=vk, d_normalizada=abs(vk - PROFESOR[var]) / (b - a) if vk is not None else None, D_minimo=dmin["D"] if dmin else None, valor_D_minimo=dmin["valor"] if dmin else None, criterios_bloqueantes_frecuentes=" · ".join(f"{k}({n})" for k, n in cods.most_common())))
    return out


def escribir(nombre: str, cab: list, filas: list) -> None:
    with open(OUT / nombre, "w", encoding="utf-8", newline="") as fh:
        esc = csv.DictWriter(fh, fieldnames=cab); esc.writeheader()
        for f in filas: esc.writerow({c: f.get(c) for c in cab})
    print(f"{nombre}: {len(filas)} filas", flush=True)


def reporte(res: list, fron: list, filas: list, t_malla: float, t_bise: float) -> None:
    """Escribe `REPORTE_M2_N1.md` en lenguaje llano (las 8 secciones pedidas)."""
    kals = [r for r in res if r["n_kalina"]]
    convs = [r for r in res if r["n_converge"]]
    cods = Counter(x for f in filas if f["convergio"] and f["clasificacion"] != "KALINA" for x in (f["codigos_falla"] or "").split(",") if x)
    ts = sorted(f["t_s"] for f in filas if f["t_s"])
    m = min(kals, key=lambda r: r["d_normalizada"]) if kals else None
    xb = {}
    for f in filas:
        if f["variable"] == "x_b" and f["valor"] < 0.55 and f["convergio"]: xb.setdefault(round(f["valor"], 6), set()).add(f["clasificacion"])
    nota = ("**Nota (x_b bajo, no preferido):** " + "; ".join(f"x_b = {v:g} → {', '.join(sorted(cs))}" for v, cs in sorted(xb.items())) + ". El proyecto considera estos valores de x_b «bajo, no preferido»; se reportan igual, sin ocultarlos.") if xb else ""
    concl = (f'Con un solo cambio **sí** se alcanza KALINA; las variables que lo logran son {", ".join(r["variable"] for r in kals)} y el cambio mínimo es {m["variable"]} = {m["valor_kalina_mas_cercano_prof"]:g} (d = {m["d_normalizada"]:.4f} de su rango).' if kals else
             f'Con un solo cambio **no** se alcanza KALINA: ninguna variable sola lo logra; las que al menos hacen converger el ciclo {("son " + ", ".join(r["variable"] for r in convs)) if convs else "no existen"}, y el criterio que queda bloqueando es {cods.most_common(1)[0][0] if cods else "ninguno"}.')
    def fila(r: dict) -> str:
        nv = r["n_converge"]
        vk = "—" if r["valor_kalina_mas_cercano_prof"] is None else f'{r["valor_kalina_mas_cercano_prof"]:g} (d = {r["d_normalizada"]:.4f})'
        dt = "—" if r["D_minimo"] is None else f'{r["D_minimo"]:g} en {r["valor_D_minimo"]:g}'
        return f'| {r["variable"]} | {("sin datos" if nv is None else "sí (" + str(nv) + ")" if nv else "no")} | {"sí" if r["n_kalina"] else "no"} | {vk} | {dt} | {r["criterios_bloqueantes_frecuentes"] or "—"} |'

    s4 = ("\n\n| Variable | Tipo | Frontera | Lado que SÍ cumple | Lado que NO cumple | Ancho final | Iteraciones | Clase del lado SÍ | D del lado SÍ | Códigos del lado SÍ |\n|---|---|---|---|---|---|---|---|---|---|\n" + "\n".join(f'| {f["variable"]} | {f["tipo"]} | {f["frontera"]} | {f["lado_si"]:g} | {f["lado_no"]:g} | {f["ancho_final"]:g} | {f["iteraciones"]} | {f["clase_lado_si"]} | {"—" if f["D_lado_si"] is None else format(f["D_lado_si"], "g")} | {f["codigos_falla_lado_si"] or "—"} |' for f in fron)) if fron else "\n\nNinguna frontera que refinar: la corrida de humo no hace bisección."
    s7 = "- Esta es una corrida de humo (2 variables × 2 valores, sin bisección): las cifras de arriba no son las de la corrida real." if HUMO else ""
    doc = f"""# REPORTE M2 nivel 1 — ¿con UN solo cambio al enunciado del profesor aparece KALINA?
## 1. La pregunta
Se cambia **una sola** variable de los datos del profesor, con las otras 10 exactamente como él las dio, y se pregunta si con ese único cambio el ciclo converge y es KALINA. Si la respuesta es sí, interesa además cuánto hay que mover esa variable.
## 2. Qué se hizo
- **La malla.** Cada una de las 10 variables se recorrió con 10 valores equiespaciados de su rango (100 corridas en total), con todo lo demás clavado en el valor del profesor: un peine de 10 dientes por variable. Eso muestra, a ojo, en qué tramo de cada variable empieza a funcionar el ciclo.
- **La bisección.** Entre cada par de valores vecinos de la malla donde cambia el resultado —de no convergir a convergir, o de no ser KALINA a serlo— se parte el intervalo por la mitad, una y otra vez, hasta dejar la frontera acotada a su tolerancia (10 kPa en las presiones, 0.5 K en las temperaturas, 0.005 en composiciones, efectividades y eficiencias). Todas las fronteras avanzan en paralelo, ronda a ronda, con los mismos 6 procesos.

## 3. Tabla por variable (primero diseño, después sitio)

| Variable | ¿Converge en algún valor? | ¿KALINA en algún valor? | Valor KALINA más cercano al profesor (d) | Mejor D | Criterio que más bloquea |
|---|---|---|---|---|---|
{chr(10).join(fila(r) for r in res)}
{nota}
## 4. Fronteras encontradas, con su precisión{s4}
## 5. Tiempos
- Malla: {t_malla:.0f} s · Bisección: {t_bise:.0f} s · Total: {t_malla + t_bise:.0f} s.
- Por punto (`t_s`): mínimo {ts[0]:.1f} s, mediana {ts[len(ts) // 2]:.1f} s, máximo {ts[-1]:.1f} s, media {sum(ts) / len(ts):.1f} s ({len(ts)} puntos).
## 6. Conclusión
{concl}
## 7. Lo que no se sabe
- La malla tiene solo 10 valores por variable: entre dos vecinos queda un hueco de (b−a)/9. Si la zona KALINA de una variable fuera más estrecha que eso y cayera justo entre dos puntos, la malla no la vería y la bisección no la buscaría.
- La bisección solo refina fronteras que la malla sí detectó entre dos vecinos consecutivos; todo lo que aparezca y desaparezca dentro de un mismo hueco queda fuera de este nivel.
- Aquí solo se cambia UNA variable a la vez; este reporte no dice nada sobre combinaciones de dos o más (eso es el nivel 2).
{s7}
## 8. Qué sigue
El nivel 2 (cambiar pares de variables) lo decide el director a partir de este reporte. Aquí no se proponen pares concretos: lo que hay son las fronteras del nivel 1 y sus cercanías al punto del profesor.
"""
    (OUT / "REPORTE_M2_N1.md").write_text(doc, encoding="utf-8"); print("REPORTE_M2_N1.md escrito", flush=True)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    print(f"M2 nivel 1 | humo={HUMO} | {N_WORKERS} workers -> {OUT}", flush=True)
    with open(OUT / "m2n1_malla.csv", "w", encoding="utf-8", newline="") as fm, open(OUT / "m2n1_biseccion.csv", "w", encoding="utf-8", newline="") as fb:
        em = csv.DictWriter(fm, fieldnames=CMALLA); em.writeheader(); fm.flush()
        eb = csv.DictWriter(fb, fieldnames=CBISE); eb.writeheader(); fb.flush()
        t0 = tm = time.perf_counter()
        malla = fase_malla(fm, em)
        t_malla = time.perf_counter() - tm
        fr = [] if HUMO else detectar(malla)
        print(f"{len(fr)} fronteras detectadas en la malla", flush=True)
        tm = time.perf_counter()
        bise = fase_biseccion(fr, fb, eb)
        t_bise = time.perf_counter() - tm
    fron = filas_fronteras(fr); escribir("m2n1_fronteras.csv", CFRON, fron)
    res = filas_resumen(malla + bise); escribir("m2n1_resumen.csv", CREST, res)
    reporte(res, fron, malla + bise, t_malla, t_bise)
    print(f"fin: {len(malla)} malla + {len(bise)} biseccion en {time.perf_counter() - t0:.0f} s -> {OUT}", flush=True)


if __name__ == "__main__": main()