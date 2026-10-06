"""M3 — `REPORTE_M3.md` en lenguaje llano, a partir de las filas de `m3_ofat.csv`.
Lo llama `m3_analisis.main()` (resumen, cruces y figuras ya escritos); también se
puede re-ejecutar solo sin recalcular el ciclo.
"""
from __future__ import annotations

import re, sys  # noqa: E401,E402
from pathlib import Path

_DIR = Path(__file__).resolve().parent
_RAIZ = _DIR.parents[1]
sys.path[:0] = [str(_RAIZ), str(_DIR)]

from m3_analisis import OUT, genu, num  # noqa: E402
from m3_ofat import ANCHOR  # noqa: E402


def _lado(m, ext, sgn):
    """Qué criterio se rompe primero al salir de la zona KALINA por un lado.

    `ext` es el borde de la zona (malla) y `sgn` el sentido: -1 = al bajar,
    +1 = al subir. Se devuelve el primer punto de la malla más allá de ese borde.
    """
    if ext is None:
        return "sin zona KALINA"
    cand = sorted([f for f in m if (f["valor"] - ext) * sgn > 0],
                  key=lambda f: abs(f["valor"] - ext))
    if not cand:
        return "— (llega al extremo del rango)"
    f = cand[0]
    return f'{f["codigos_falla"] or "sin código"} ({f["clasificacion"]})'


def _tabla(res, g):
    filas = ["| variable | rango [a, b] | E en A\\* | Δη (pp) | zona KALINA (malla) | al bajar | al subir |",
             "|---|---|---|---|---|---|---|"]
    for r in res:
        a, b, m, _ = g[r["variable"]]
        E = "—" if r["E_eta"] is None else f'{r["E_eta"]:.3f}'
        if r["E_eta"] is None:
            E += f' ({r["motivo_E"]})'
        de = "—" if r["delta_eta"] is None else f'{r["delta_eta"] * 100:.2f}'
        z = ("vacía" if r["kalina_desde"] is None
             else f'{r["kalina_desde"]:g} … {r["kalina_hasta"]:g}')
        filas.append(f'| {r["variable"]} | [{a:g}, {b:g}] | {E} | {de} | {z} | '
                     f'{_lado(m, r["kalina_desde"], -1)} | {_lado(m, r["kalina_hasta"], +1)} |')
    return "\n".join(filas)


def _fronteras(cruces, g):
    cerc = []
    for c in cruces:
        if c["tipo"] == "margen":
            a, b, _, _ = g[c["variable"]]
            cerc.append((abs(c["v_cruce"] - ANCHOR[c["variable"]]) / (b - a), c))
    if not cerc:
        return ("No cambió de signo ningún margen entre dos puntos consecutivos de la "
                "malla: no hay frontera interpolada dentro del rango medido.")
    cerc.sort(key=lambda t: t[0])
    filas = ["| variable | margen | valor de cruce | valor de A\\* | distancia (fracción del rango) |",
             "|---|---|---|---|---|"]
    for dist, c in cerc:
        filas.append(f'| {c["variable"]} | {c["criterio"]} | {c["v_cruce"]:g} | '
                     f'{ANCHOR[c["variable"]]:g} | {dist:.3f} |')
    return "\n".join(filas)


def _rankings(res):
    conE = sorted([r for r in res if r["E_eta"] is not None], key=lambda r: -abs(r["E_eta"]))
    conD = sorted([r for r in res if r["delta_eta"] is not None], key=lambda r: -r["delta_eta"])
    rkE = "\n".join(f'{i}. **{r["variable"]}** — |E| = {abs(r["E_eta"]):.3f}'
                    for i, r in enumerate(conE, 1)) or "ninguna: no se pudo calcular ninguna E"
    rkD = "\n".join(f'{i}. **{r["variable"]}** — Δη = {r["delta_eta"] * 100:.2f} pp'
                    for i, r in enumerate(conD, 1)) or "ninguna: no hay Δη calculable"
    pe = {r["variable"]: i for i, r in enumerate(conE, 1)}
    pd = {r["variable"]: i for i, r in enumerate(conD, 1)}
    difs = [f'- **{n}** pasa de la {pe[n]}ª posición por |E| a la {pd[n]}ª por Δη.'
            for n in sorted(set(pe) & set(pd)) if abs(pe[n] - pd[n]) >= 2]
    sinE = [f'{r["variable"]} ({r["motivo_E"]})' for r in res if r["E_eta"] is None]
    return conE, conD, rkE, rkD, difs, sinE


def _tiempo():
    """`(corridas, segundos)` leídos de stdout.txt (Tee-Object: utf-16 o utf-8)."""
    p = OUT / "stdout.txt"
    if not p.exists():
        return None
    for enc in ("utf-8", "utf-16"):
        try:
            m = re.search(r"fin: (\d+) corridas en (\d+) s", p.read_bytes().decode(enc))
        except (UnicodeDecodeError, ValueError):
            continue
        if m:
            return m
    return None


def _doc(res, cruces, filas, ancla, g):
    conE, conD, rkE, rkD, difs, sinE = _rankings(res)
    eta0 = "no calculada" if ancla["eta"] is None else f'{ancla["eta"]:.4f}'
    nk = sum(1 for f in filas if f["clasificacion"] == "KALINA")
    ngen = sum(1 for f in filas if genu(f))
    fuera = sum(1 for f in filas if f["fuera_rango"] == "True")
    ncamb = sum(1 for c in cruces if c["tipo"] == "clase")
    zonas = [r for r in res if r["kalina_desde"] is not None]
    ts = sorted(v for v in (num(f.get("t_s")) for f in filas) if v is not None)
    mout = _tiempo()
    pared = (f'La corrida completa ({mout.group(1)} corridas) tardó {mout.group(2)} s.'
             if mout else "El tiempo total de la corrida no está en stdout.txt.")
    if ts:
        pared += (f' Por punto (`t_s`): mínimo {ts[0]:.1f} s, mediana {ts[len(ts) // 2]:.1f} s, '
                  f'máximo {ts[-1]:.1f} s, media {sum(ts) / len(ts):.1f} s ({len(ts)} puntos).')
    topE = conE[0] if conE else None
    topD = conD[0] if conD else None
    dtxt = ("\n" + "\n".join(difs) if difs else
            "\nNinguna variable cambia más de una posición entre los dos rankings.")
    stxt = f"\n\nVariables sin E: {'; '.join(sinE)}." if sinE else ""
    conc = (f'La variable que más mueve η **pegada al ancla** es **{topE["variable"]}** '
            f'(elasticidad |E| = {abs(topE["E_eta"]):.3f}), y la que más la mueve '
            f'**recorriendo todo su rango** es **{topD["variable"]}** '
            f'(Δη = {topD["delta_eta"] * 100:.2f} pp).') if topE and topD else \
        "No hay suficientes puntos genuinos para cerrar un ranking."
    ztxt = (f"La zona KALINA alrededor de A\\* se pudo medir en {len(zonas)} de las 10 "
            "variables" + ("; en las demás queda vacía porque ni la malla ni el ancla "
                           "cercana son KALINA." if len(zonas) < 10 else " (detalle en §3).")
            ) if zonas else \
        "Ninguna variable tiene zona KALINA alrededor del ancla con esta malla."
    return f"""# REPORTE M3 — sensibilidad local (una variable a la vez) alrededor de A\\*
## 1. La pregunta
Hay 10 datos que definen el ciclo: dos temperaturas, dos presiones, la composición y cinco eficiencias. La pregunta es: **si muevo UNA sola variable dentro de su rango y dejo las otras nueves exactamente en el punto A\\*, ¿cuánto cambia la eficiencia η y en qué momento el ciclo deja de ser KALINA?** De ahí sale un ranking de qué dato conviene cuidar más.
## 2. Qué se hizo, en simple
- **El punto de partida (A\\*).** `T_fuente = 403.0 K`, `P_baja = 563.6363636363637 kPa` y las otras ocho variables tal como las dio el profesor. Ahí el ciclo quedó **{ancla["clasificacion"]}** con η = {eta0}.
- **La malla (OAT).** Por cada variable se recorrieron 15 valores repartidos por igual entre su rango (1.º valor = extremo inferior, 15.º = extremo superior), con las otras nueve quietas en A\\*: 10 × 15 = 150 corridas.
- **Los dos vecinos.** Para la elasticidad se corrieron además A\\* ± h con h = 1 % del rango de cada variable: 10 × 2 = 20 corridas. Más el ancla sola: **1 + 150 + 20 = 171 corridas**, con 5 procesos y el motor `teqp`.
- **Qué cuenta como punto bueno (genuino).** Solo KALINA, CORREGIBLE e INVIABLE. Una fila que el solver cerró pero que el clasificador marca NO_CONVERGIO es un punto fijo espurio (N2) y no cuenta para nada.
- **Qué se midió.** Δη = η mayor − η menor dentro de la malla; E = qué tanto cambia η (en tanto por uno) ante un empujoncito del 1 % en A\\*; las fronteras se interpolan linealmente entre los dos puntos vecinos donde un margen cambia de signo; y la *zona KALINA* es el tramo de valores de la malla, contiguo al valor de A\\*, donde la clase sigue siendo KALINA.
- **Salidas.** `m3_ofat.csv` ({len(filas)} filas), `m3_resumen.csv` (10 filas, una por variable), `m3_cruces.csv` ({len(cruces)} filas: {ncamb} cambios de clase y {len(cruces) - ncamb} cruces de margen) y las tres figuras de §6.
## 3. Una tabla por variable

{_tabla(res, g)}
## 4. Ranking de influencia sobre η

**Por elasticidad |E| en A\\* (pegado al ancla):**

{rkE}

**Por Δη en todo el rango (de un extremo a otro de la malla):**

{rkD}

Las dos listas **no tienen por qué coincidir**: E mide solo a un 1 % del rango de A\\*, mientras Δη mide los 15 puntos de la malla, que cubren el rango completo. Una variable puede ser empinada pegada al ancla y aplanarse lejos (o al revés), y Δη además crece con el ancho del rango de esa variable.
{dtxt}{stxt}
Recuerde: las diferencias de η menores que 0.4–0.7 pp no son concluyentes (§9).
## 5. Las fronteras más cercanas al ancla

Distancia entre el valor interpolado de cada frontera y el valor de A\\* en esa variable, medida como fracción del rango de la variable (0 = justo en el ancla, 1 = a todo lo ancho del rango):

{_fronteras(cruces, g)}

Entre puntos consecutivos de la malla hubo **{ncamb} cambios de clase** (registrados en `m3_cruces.csv` con las dos clases y el par de valores).
## 6. Figuras

Tornado (Δη dentro del rango, de mayor a menor):

![Tornado](m3_tornado.png)

Elasticidad E en A\\* (n/d = no se pudo calcular, con el motivo en §3):

![Elasticidad](m3_elasticidad.png)

Curvas η por variable: cada punto con el color de su clase, la línea punteada marca el valor de A\\*; los puntos sin η (no convergidos) se dibujan como × sobre el eje:

![Curvas](m3_curvas.png)
## 7. Tiempos
{pared}
## 8. Conclusión
{conc}
De los {len(filas)} puntos corridos, {ngen} son genuinos y {nk} son KALINA.
{ztxt}
El detalle de qué criterio se rompe primero por cada lado está en la columna de §3, y qué tan al filo está A\\* se ve en §5.
## 9. Lo que no se sabe
- **OAT no ve interacciones.** Cada variable se mueve sola con las otras nueve en A\\*: dos variables que se compensan entre sí no aparecen en este cuadro. Por eso el siguiente paso (M4) es obligatorio.
- **Las diferencias de η menores que 0.4–0.7 pp no son concluyentes.** Es la banda de incertidumbre del modelo de propiedades (G4-01): cualquier diferencia a esa escala puede ser ruido, no un efecto real.
- **Hay puntos fuera del rango confiable:** {fuera} de los {len(filas)} corridos (temperaturas de líquido por encima de 420 K, sin respaldo experimental). Sus η hay que tomarlas con pinzas.
## 10. Qué sigue
M4 (sensibilidad global con muestreo LHS y análisis RSA/PAWN/PRCC). Aquí no se propone ningún valor concreto: las tablas de §3 y §5 son insumos para que el director decida.
"""


def generar(res, cruces, filas, ancla, g) -> None:
    (OUT / "REPORTE_M3.md").write_text(_doc(res, cruces, filas, ancla, g), encoding="utf-8")
    print("REPORTE_M3.md escrito", flush=True)


if __name__ == "__main__":
    raise SystemExit("Importar desde m3_analisis.py; la corrida es m3_analisis.py")
