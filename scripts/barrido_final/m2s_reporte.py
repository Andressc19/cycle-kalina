"""M2S — resúmenes, figura y `REPORTE_M2S.md` (TASK_CONTEXT final_M2S)."""
from __future__ import annotations
import csv, sys
from collections import Counter
from pathlib import Path
_DIR = Path(__file__).resolve().parent
_RAIZ = _DIR.parents[1]
sys.path[:0] = [str(_RAIZ), str(_DIR)]
import matplotlib  # noqa: E402
matplotlib.use("Agg")
from matplotlib.figure import Figure  # noqa: E402
import m2s_corrida as cor  # noqa: E402
CRES = ["base", "T_sumidero", "n_genuinos", "n_kalina", "n_N2", "P_baja_min_kalina",
        "eta_min_kalina", "B_verificado_min_kalina", "fuera_rango_min_kalina",
        "eta_max_kalina", "P_baja_eta_max_kalina", "bloqueantes_genuinos", "codigos_bloqueo"]
CKAL = ["base", "T_sumidero_val", "P_baja_val", "eta", "Wnet", "m_O1", "m_O2", "D",
        "fuera_rango", "detalle_rango", "B_verificado", "B_dh4s"]
HUS = ("Húsavík (sumidero de 5 °C, piso de 10 °C, P_baja de 670–690 kPa y η de "
       "12.7–13.4 %) **es otro ciclo**: x_b = 0.82 y P_alta = 3300 kPa, así que "
       "la comparación es de **tendencia, no de valor**.")
def filas_kalina(todo: list) -> list:
    """KALINA de malla + bisección, sin duplicados por (base, T, P_baja)."""
    out, visto = [], set()
    for f in todo:
        k = (f["base"], f["T_sumidero_val"], f["P_baja_val"])
        if cor.es_kalina(f) and k not in visto:
            visto.add(k)
            out.append({c: f.get(c) for c in CKAL})
    return sorted(out, key=lambda r: (r["base"], r["T_sumidero_val"], r["P_baja_val"]))
def filas_resumen(todo: list) -> list:
    """Una fila por (base, T_sumidero): conteos, mínimos, máximos y bloqueos."""
    out = []
    for base in cor.BASES:
        for Ts in cor.TSUM:
            g = [f for f in todo if f["base"] == base and f["T_sumidero_val"] == Ts]
            gen = [f for f in g if cor.genuina(f)]
            kal = sorted([f for f in g if cor.es_kalina(f)], key=lambda f: f["P_baja_val"])
            k0 = kal[0] if kal else {}
            ce = [f for f in kal if f["eta"] is not None]
            km = max(ce, key=lambda f: f["eta"]) if ce else {}
            blo = [f for f in gen if not cor.es_kalina(f)]
            cl = Counter(f["clasificacion"] for f in blo)
            cd = Counter(x for f in blo for x in (f["codigos_falla"] or "").split(",") if x)
            fil = dict(base=base, T_sumidero=Ts, n_genuinos=len(gen), n_kalina=len(kal),
                       n_N2=sum(1 for f in g if f.get("convergio") is True
                                and f.get("clasificacion") == "NO_CONVERGIO"),
                       P_baja_min_kalina=k0.get("P_baja_val"), eta_min_kalina=k0.get("eta"),
                       B_verificado_min_kalina=k0.get("B_verificado"),
                       fuera_rango_min_kalina=k0.get("fuera_rango"),
                       eta_max_kalina=km.get("eta"), P_baja_eta_max_kalina=km.get("P_baja_val"),
                       bloqueantes_genuinos=" · ".join(f"{k}({n})" for k, n in cl.most_common()),
                       codigos_bloqueo=" · ".join(f"{k}({n})" for k, n in cd.most_common()))
            out.append(fil)
    return out
def escribir(nombre: str, cab: list, filas: list) -> None:
    """Un CSV con cabecera y una fila por `filas`, en `cor.OUT`."""
    with open(cor.OUT / nombre, "w", encoding="utf-8", newline="") as fh:
        esc = csv.DictWriter(fh, fieldnames=cab); esc.writeheader()
        for f in filas:
            esc.writerow({c: f.get(c) for c in cab})
    print(f"{nombre}: {len(filas)} filas", flush=True)
def figura(res: list) -> None:
    """`m2s_pbaja_eta.png`: η y P_baja mínimas KALINA contra el clima."""
    fig = Figure(figsize=(9.5, 4.2), dpi=140); axs = fig.subplots(1, 2)
    for base in cor.BASES:
        ok = [r for r in res if r["base"] == base and r["P_baja_min_kalina"] is not None]
        for ax, k in zip(axs, ("eta_min_kalina", "P_baja_min_kalina")):
            ax.plot([r["T_sumidero"] for r in ok], [r[k] for r in ok], marker="o", label=base)
    for ax, (lab, tit) in zip(axs, (("η en la P_baja mínima KALINA", "η vs clima"),
                                    ("P_baja mínima KALINA (kPa)", "P_baja vs clima"))):
        ax.set(xlabel="T_sumidero (K)", ylabel=lab, title=tit)
        ax.grid(True, alpha=0.3); ax.legend(title="base")
    fig.tight_layout(); fig.savefig(cor.OUT / "m2s_pbaja_eta.png")
    print("m2s_pbaja_eta.png escrito", flush=True)
def _celdas(res: list, b: str, Ts: float) -> list:
    """La pareja (P_baja mínima KALINA, η) de una celda de tabla, o «—»."""
    r = next(x for x in res if x["base"] == b and x["T_sumidero"] == Ts)
    return ["—", "—"] if r["P_baja_min_kalina"] is None else [
        f'{r["P_baja_min_kalina"]:g}', f'{r["eta_min_kalina"]:.4f}']
def _tabla(res: list) -> str:
    """§3: filas = T_sumidero; columnas = P_baja mínima KALINA y su η, por base."""
    cab = "| T_sumidero (K) | " + " | ".join(f"{b} P_baja (kPa) | {b} η" for b in cor.BASES) + " |"
    sep = "|" + "---|" * (1 + 2 * len(cor.BASES))
    filas = [f"| {Ts:g} | " + " | ".join(sum((_celdas(res, b, Ts) for b in cor.BASES), [])) + " |" for Ts in cor.TSUM]
    return "\n".join([cab, sep] + filas)
def _s4(res: list) -> str:
    """§4: ¿el sumidero frío solo (B4) vuelve KALINA al profesor?"""
    b4 = [r for r in res if r["base"] == "B4"]
    ok = [r for r in b4 if r["n_kalina"]]
    if not ok:
        bloq = "; ".join(f'{r["T_sumidero"]:g} K → {r["bloqueantes_genuinos"] or "sin criterio"}'
                         + (f' [{r["codigos_bloqueo"]}]' if r["codigos_bloqueo"] else "") for r in b4)
        return (f"**No.** Con el profesor exacto (B4) **ninguno** de los {len(b4)} "
                f"climas probados da un punto KALINA: {bloq}.")
    det = "; ".join(f'{r["T_sumidero"]:g} K → P_baja {r["P_baja_min_kalina"]:g} kPa, '
                    f'η = {r["eta_min_kalina"]:.4f}' for r in ok)
    return (f"**Sí.** El sumidero frío solo basta: B4 alcanza "
            f"{sum(r['n_kalina'] for r in ok)} punto(s) KALINA en {len(ok)} de "
            f"{len(b4)} climas — {det}.")
def _pasos(res: list) -> list:
    """§5, por base: Δη al bajar el sumidero de un nivel al siguiente."""
    lineas = []
    for b in cor.BASES:
        rs = [r for r in res if r["base"] == b]        # ascendente en T
        pasos = []
        for frio, cal in zip(rs, rs[1:]):
            dt = cal["T_sumidero"] - frio["T_sumidero"]
            a, c = frio["eta_min_kalina"], cal["eta_min_kalina"]   # η fría y η caliente
            txt = f'{cal["T_sumidero"]:g} → {frio["T_sumidero"]:g} K (ΔT = {dt:.3f} K)'
            pasos.append(f"{txt}: — (sin KALINA en un extremo)"
                         if a is None or c is None else f"{txt}: η {a - c:+.5f}")
        lineas.append((b, pasos))
    return lineas
def _s8(res: list, kal: list) -> str:
    """§8: qué bases alcanzan KALINA y cómo cambia η con el clima."""
    ok = [b for b in cor.BASES if any(r["n_kalina"] for r in res if r["base"] == b)]
    lin = [f"- **{len(ok)} de {len(cor.BASES)} bases** alcanzan KALINA "
           f"({', '.join(ok) if ok else 'ninguna'}); hay **{len(kal)}** puntos "
           f"KALINA sin duplicados en total."]
    for b in ok:
        rs = [r for r in res if r["base"] == b and r["eta_min_kalina"] is not None]
        if len(rs) >= 2:
            frio, cal = rs[0], rs[-1]
            lin.append(f"- **{b}**: al bajar el sumidero de {cal['T_sumidero']:g} a "
                       f"{frio['T_sumidero']:g} K, η de {cal['eta_min_kalina']:.4f} a "
                       f"{frio['eta_min_kalina']:.4f} ({frio['eta_min_kalina'] - cal['eta_min_kalina']:+.5f}) "
                       f"y la P_baja mínima de {cal['P_baja_min_kalina']:g} a "
                       f"{frio['P_baja_min_kalina']:g} kPa.")
    return "\n".join(lin)
def _filas_hus(res: list) -> list:
    return [f"| {b} | {Ts:g} | " + " | ".join(_celdas(res, b, Ts)) + " |"
            for b in cor.BASES for Ts in (278.15, 283.15)]
def reporte(res, kal, todo, t_malla, t_bise) -> None:
    """Escribe `REPORTE_M2S.md` en lenguaje llano (las 10 secciones pedidas)."""
    ts = sorted(f["t_s"] for f in todo if f.get("t_s"))
    nk, fk = len(kal), [k for k in kal if k["fuera_rango"]]
    g278 = [f for f in todo if f["T_sumidero_val"] == 278.15]
    mal278 = [f for f in g278 if not cor.genuina(f)]
    s5 = "\n".join(f"- **{b}**: " + " · ".join(p) for b, p in _pasos(res))
    s7 = (f"- Malla: {t_malla:.0f} s · Bisección: {t_bise:.0f} s · Total: "
          f"{t_malla + t_bise:.0f} s.\n"
          f"- Por punto (`t_s`): mínimo {ts[0]:.1f} s, mediana {ts[len(ts) // 2]:.1f} s, "
          f"máximo {ts[-1]:.1f} s, media {sum(ts) / len(ts):.1f} s ({len(ts)} puntos).")
    s9 = [(f"- {len(fk)} de los {nk} puntos KALINA quedan **fuera del rango confiable** "
           "(IAPWS G4-01): " + "; ".join(f'{k["base"]} {k["T_sumidero_val"]:g} K / '
                                         f'{k["P_baja_val"]:g} kPa' for k in fk) + "."
           if fk else (f"- Ninguno de los {nk} puntos KALINA queda fuera del rango "
                       "confiable (IAPWS G4-01)." if nk else "- No se encontró ningún KALINA.")),
          (f"- En el clima más frío (278.15 K) {len(mal278)} de {len(g278)} puntos no son "
           f"genuinos (N2 o no convergen): son los que quedan más cerca del límite del motor."),
          ("- La malla de P_baja tiene 10 valores entre 150 y 1500 kPa (paso de 150 kPa): una "
           "zona KALINA más estrecha que eso no aparece ni en la malla ni en la bisección.")]
    if cor.HUMO:
        s9.append("- Esta es una corrida de humo (1 base × 2 T_sumidero × 2 P_baja, sin "
                  "bisección): las cifras de arriba NO son las de la corrida real.")
    doc = f"""# REPORTE M2S — efecto de un sumidero frío con P_baja libre
## 1. La pregunta
Si el sitio es más frío y el criterio de cavitación (O2) se evalúa con **ese** clima —el piso de O2 es `T_sumidero`, no el piso tropical heredado—, ¿cuánto baja la P_baja necesaria para KALINA y cuánto sube η?
## 2. Qué se hizo
- **Cuatro bases**, con todo lo demás como `comun.PROFESOR`: B1 `T_fuente` = 403.0 K (el ancla de M3); B2 `T_fuente` = 420.0 K (el KALINA de mayor η de M2); B3 `eps_hrvg` = 0.40 (conserva la fuente de 623.15 K, la ruta de M2R); B4 **ningún cambio** (el profesor exacto).
- **Climas**: `T_sumidero` ∈ {{278.15, 283.15, 288.15, 293.15, 300.032917}} K, **siempre con `t_amb_diseno = T_sumidero`**: el piso de O2 sigue al clima del sitio.
- **Malla**: `P_baja` ∈ `numpy.linspace(150, 1500, 10)` → 4 × 5 × 10 = **200 corridas** con 5 procesos, cada fila con flush en `m2s_malla.csv`.
- **Bisección**: por cada (base, T_sumidero), sobre P_baja, en cada par de vecinos donde cambia «es KALINA» o donde cambia `m_O2 >= 0` con ambos vecinos genuinos; tolerancia 10 kPa, máximo 7 iteraciones, rondas paralelas. Filas en `m2s_biseccion.csv`.
- **Punto genuino**: `clasificacion ∈ {{KALINA, CORREGIBLE, INVIABLE}}`. Una fila con `convergio=True` y `NO_CONVERGIO` es espuria (N2) y se trata como NO genuina en conteos, fronteras y conclusiones.
- **Salidas**: `m2s_resumen.csv`, `m2s_kalina.csv` (KALINA sin duplicados), la figura `m2s_pbaja_eta.png` y este reporte.
## 3. Tabla por base (filas: T_sumidero; columnas: P_baja mínima KALINA y su η)

{_tabla(res)}
## 4. ¿El sumidero frío solo (B4) vuelve KALINA al profesor?
{_s4(res)}
## 5. Cuánto sube η por cada paso de 5 K de sumidero más frío
Variación de η en el punto de P_baja mínima KALINA al bajar el sumidero de un nivel al siguiente (los pasos de 278.15 a 293.15 K son exactamente de 5 K; el último, de 293.15 a 300.032917 K, mide 6.883 K):

{s5}
## 6. Comparación con Húsavík
{HUS}
Nuestro KALINA en los climas más fríos, contra su sumidero de 5 °C con piso de 10 °C:

| Base | T_sumidero (K) | P_baja mínima KALINA (kPa) | η |
|---|---|---|---|
{chr(10).join(_filas_hus(res))}
## 7. Tiempos
{s7}
## 8. Conclusión
{_s8(res, kal)}
## 9. Lo que no se sabe
{chr(10).join(s9)}
## 10. Qué sigue
El siguiente paso lo decide el director con la tabla de §3 y la figura `m2s_pbaja_eta.png` (una curva por base: η y P_baja mínimas contra el clima). Aquí no se proponen valores concretos: solo lo medido en la malla y acotado por la bisección.
"""
    (cor.OUT / "REPORTE_M2S.md").write_text(doc, encoding="utf-8")
    print("REPORTE_M2S.md escrito", flush=True)
def generar(malla, bise, fr, t_malla, t_bise) -> None:
    """CSVs, figura y reporte, a partir de las filas de las dos fases."""
    todo = malla + bise
    kal = filas_kalina(todo); escribir("m2s_kalina.csv", CKAL, kal)
    res = filas_resumen(todo); escribir("m2s_resumen.csv", CRES, res)
    figura(res); reporte(res, kal, todo, t_malla, t_bise)
if __name__ == "__main__":
    raise SystemExit("Importar y llamar generar(); la corrida es m2s_corrida.py")
