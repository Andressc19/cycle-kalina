# -*- coding: utf-8 -*-
"""A3 · Utilidades compartidas de las figuras de la campaña final.

Carga la tabla canónica, grafica por clase (forma+color, huecos para fuera de
rango), dibuja tiras y paneles, y empaqueta el pie y la salida estándar.
"""
import os

import numpy as np
import pandas as pd

from estilo import (COLOR_CLASE, ORDEN_CLASE, MARCADOR_CLASE, recuadro_condiciones)
from nombres import ETIQUETA_CLASE, NOMBRE

PUNTOS = "analisis_final/01_datos/todos_los_puntos.csv"

# Orden de presentación de las variables (suites OAT y CDF).
SEC_VAR = ["T_fuente", "T_sumidero", "P_alta", "P_baja", "x_b",
           "eta_t", "eta_p", "eps_hrvg", "eps_reg", "eps_cond"]


def _bool(x):
    """Interpreta un flag de la tabla canónica como booleano."""
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return False
    if isinstance(x, (bool, np.bool_)):
        return bool(x)
    if isinstance(x, (int, float, np.integer, np.floating)):
        return bool(x)
    return str(x).strip().lower() in ("true", "1", "sí", "si", "verdadero")


def cargar():
    """Tabla canónica con flags normalizados a bool."""
    df = pd.read_csv(PUNTOS)
    for c in ("genuino", "wnet_pos", "fuera_rango", "omitido"):
        if c in df.columns:
            df[c] = df[c].map(_bool)
    return df


def contar_clases(sub):
    """Cuenta por clase de trazo, incluido OMITIDO."""
    n = {}
    for c in ORDEN_CLASE:
        n[c] = int((sub["clase_trazo"] == c).sum())
    if "omitido" in sub.columns:
        n["OMITIDO"] = int(sub["omitido"].sum())
    return n


def dispersion(ax, sub, x, y, s=14, zorder=3, alfa=0.9):
    """Puntos de una dispersión, una serie por clase.

    OMITIDO nunca se dibuja; los fuera de rango van huecos. KALINA encima.
    """
    sub = sub[~sub["omitido"]]
    for c in ORDEN_CLASE[::-1]:
        s2 = sub[sub["clase_trazo"] == c]
        if s2.empty:
            continue
        hueco = s2["fuera_rango"]
        ax.scatter(s2.loc[~hueco, x], s2.loc[~hueco, y], s=s, alpha=alfa,
                   color=COLOR_CLASE[c], marker=MARCADOR_CLASE[c],
                   label=f"{ETIQUETA_CLASE[c]} (n = {len(s2)})", zorder=zorder)
        if MARCADOR_CLASE[c] == "x":     # la ✕ no tiene relleno: hueco no aplica
            ax.scatter(s2.loc[hueco, x], s2.loc[hueco, y], s=s, alpha=alfa,
                       color=COLOR_CLASE[c], marker="x", zorder=zorder)
        else:
            ax.scatter(s2.loc[hueco, x], s2.loc[hueco, y], s=s, alpha=alfa,
                       facecolors="none", edgecolors=COLOR_CLASE[c],
                       marker=MARCADOR_CLASE[c], zorder=zorder)


def tira(ax, sub, x, y=0.0, s=16, etiquetas=True):
    """Tira de clases (FIG-M02-01 y M02R-n1): x = valor de la variable movida; cada clase
    en su propia fila (KALINA arriba). Antes se repartían en una diagonal que parecía tendencia."""
    sub = sub[~sub["omitido"]]
    filas = {c: i for i, c in enumerate(ORDEN_CLASE[::-1])}      # N2 = 0 … KALINA = 4
    for c in ORDEN_CLASE[::-1]:
        s2 = sub[sub["clase_trazo"] == c]
        if s2.empty:
            continue
        jit = (np.arange(len(s2)) % 3 - 1) * 0.12                   # leve, solo para no tapar
        ax.scatter(s2[x], filas[c] + jit, s=s, color=COLOR_CLASE[c],
                   marker=MARCADOR_CLASE[c], alpha=0.9,
                   label=f"{ETIQUETA_CLASE[c]} (n = {len(s2)})")
    ax.set_ylim(-0.6, len(filas) - 0.4)
    ax.set_yticks(list(filas.values()))
    ax.set_yticklabels([ETIQUETA_CLASE[c] if etiquetas else "" for c in filas], fontsize=6.5)


def sin_eta_sobre_eje(ax, sub, x, ymin, s=16):
    """Sin W_net > 0 (o no genuinos) como ✕ sobre el eje x (regla 7)."""
    sub = sub[~sub["omitido"]]
    sin = sub[~(sub["genuino"] & sub["wnet_pos"])]
    for c in ORDEN_CLASE[::-1]:
        s2 = sin[sin["clase_trazo"] == c]
        if s2.empty:
            continue
        ax.scatter(s2[x], np.full(len(s2), ymin), s=s, color=COLOR_CLASE[c],
                   marker=MARCADOR_CLASE[c], alpha=0.9)


def titulo(ax, linea1, linea2, f1=9, f2=8):
    """Título de dos líneas (regla 3): 1.ª conclusión; 2.ª, más pequeña,
    'Bloque <b> · <caso(s)>'. Ambas ancladas a la izquierda, sobre el panel.
    """
    ax.set_title(linea1, fontsize=f1, loc="left")
    if linea2:
        ax.text(0.0, 1.13, linea2, transform=ax.transAxes, fontsize=f2,
                va="bottom", ha="left")


def titulo_fig(fig, linea1, linea2, f1=10, f2=8):
    """Título de dos líneas para figuras multipanel (en la figura, no en cada eje)."""
    fig.text(0.5, 0.995, linea1, ha="center", va="top", fontsize=f1)
    fig.text(0.5, 0.962, linea2, ha="center", va="top", fontsize=f2)
    fig._multipanel = True   # estilo.guardar deja sitio arriba (título/leyenda) y abajo (recuadro)


def texto_condiciones_corto(ax, texto, n_lineas=3, ancho=70):
    """Recuadro de condiciones (regla 4): el texto se parte en líneas de ≤ `ancho`
    caracteres y se recorta a `n_lineas` + 1 (el texto completo va en el pie).
    Sin el corte, una línea larga ensancha la figura al guardar con bbox 'tight'."""
    import textwrap
    lineas = []
    for l in texto.splitlines():
        if l.strip():
            lineas += textwrap.wrap(l, ancho)
    tope = n_lineas + 1
    if len(lineas) > tope:
        lineas = lineas[:tope]
        lineas[-1] = lineas[-1][:ancho - 18].rstrip("; ") + " … (ver pie)"
    recuadro_condiciones(ax, "\n".join(lineas))


def recuadro_oat(ax, id_subcasos, n_lineas=3):
    """Recuadro desde condiciones_texto (pies.condiciones_texto), recortado."""
    from pies import condiciones_texto
    texto_condiciones_corto(ax, condiciones_texto(id_subcasos), n_lineas)


def recuadro_fig(fig, id_subcasos, n_lineas=2, ancho=190):
    """Recuadro de condiciones para figuras de varios paneles: va centrado al pie de la
    figura (no dentro de un panel, para no deformar la rejilla)."""
    import textwrap
    from pies import condiciones_texto
    lineas = []
    for l in condiciones_texto(id_subcasos).splitlines():
        if l.strip():
            lineas += textwrap.wrap(l, ancho)
    if len(lineas) > n_lineas + 1:
        lineas = lineas[:n_lineas + 1]
        lineas[-1] = lineas[-1][:ancho - 18].rstrip("; ") + " … (ver pie)"
    fig.text(0.5, 0.005, "\n".join(lineas), ha="center", va="bottom", fontsize=7,
             bbox=dict(boxstyle="round", fc="white", ec="0.7"))
    fig._multipanel = True


def leyenda_fig(fig, sub):
    """Leyenda única de la figura con el n TOTAL por clase (no el de un panel)."""
    import matplotlib.pyplot as plt
    n = contar_clases(sub)
    h = [plt.Line2D([0], [0], marker=MARCADOR_CLASE[c], ls="", color=COLOR_CLASE[c],
                    label=f"{ETIQUETA_CLASE[c]} (n = {n[c]})") for c in ORDEN_CLASE if n.get(c)]
    fig.legend(handles=h, loc="upper center", bbox_to_anchor=(0.5, 0.94), ncol=len(h),
               fontsize=8, frameon=False)


def guardar_clases(carpeta, nombre, n):
    """Conteos por clase de puntos dibujados, para el verificador (a3_verificar)."""
    import json
    os.makedirs(f"analisis_final/03_figuras/{carpeta}", exist_ok=True)
    with open(f"analisis_final/03_figuras/{carpeta}/{nombre}_clases.json",
              "w", encoding="utf-8") as f:
        json.dump(n, f, ensure_ascii=False, indent=1)


def guardar_fig(fig, carpeta, nombre, pie):
    """Guarda PNG+SVG+pie.md en 03_figuras/<carpeta>/<nombre>."""
    os.makedirs(f"analisis_final/03_figuras/{carpeta}", exist_ok=True)
    from estilo import guardar
    guardar(fig, f"analisis_final/03_figuras/{carpeta}/{nombre}", pie)
