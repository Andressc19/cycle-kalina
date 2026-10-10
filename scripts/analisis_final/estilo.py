# -*- coding: utf-8 -*-
"""A3 · Estilo común de las figuras (METODOLOGIA_ANALISIS_RESULTADOS §4.3).

Bloque de código de la metodología, tal cual, más las dos líneas pedidas:
COLOR_CLASE["OMITIDO"] y MARCADOR_CLASE["OMITIDO"].
"""
import matplotlib.pyplot as plt

COLOR_CLASE = {"KALINA": "#2E7D32", "CORREGIBLE": "#EF8A17",
               "INVIABLE": "#C9A227", "NO_CONVERGIO": "#C62828", "N2": "#9E9E9E"}
ORDEN_CLASE = ["KALINA", "CORREGIBLE", "INVIABLE", "NO_CONVERGIO", "N2"]
MARCADOR_CLASE = {"KALINA": "o", "CORREGIBLE": "^", "INVIABLE": "s",
                  "NO_CONVERGIO": "x", "N2": "x"}   # forma + color: se entiende sin color

# Pedido del TASK_CONTEXT af-A3: OMITIDO no se dibuja, pero se colorea y cuenta.
COLOR_CLASE["OMITIDO"] = "#BDBDBD"
MARCADOR_CLASE["OMITIDO"] = "."


def aplicar_estilo():
    plt.rcParams.update({"figure.figsize": (6.3, 3.9), "figure.dpi": 150,
                         "savefig.dpi": 300, "font.size": 9, "axes.grid": True,
                         "grid.alpha": 0.3, "axes.spines.top": False,
                         "axes.spines.right": False, "legend.frameon": False})


def clase_trazo(row):
    """Clase para colorear: separa N2 (convergio=True pero NO_CONVERGIO)."""
    if row["clasificacion"] == "NO_CONVERGIO" and bool(row.get("convergio")):
        return "N2"
    return row["clasificacion"]


ETIQUETA_CLASE = {"KALINA": "KALINA", "CORREGIBLE": "Corregible", "INVIABLE": "Inviable",
                  "NO_CONVERGIO": "No convergió", "N2": "Falso convergido (N2)"}


def recuadro_condiciones(ax, texto):
    """Recuadro con el bloque y los datos fijos esenciales, dentro de la figura."""
    ax.text(0.99, 0.01, texto, transform=ax.transAxes, ha="right", va="bottom",
            fontsize=7, bbox=dict(boxstyle="round", fc="white", ec="0.7", alpha=0.9))


def guardar(fig, ruta_sin_ext, pie):
    """Guarda PNG + SVG y el pie de figura en <ruta>.pie.md (mismo texto para informe y Excel)."""
    if getattr(fig, "_multipanel", False):
        fig.tight_layout(rect=(0, 0.07, 1, 0.89))   # sitio para título, leyenda y recuadro
    else:
        fig.tight_layout()
    for ext in ("png", "svg"):
        fig.savefig(f"{ruta_sin_ext}.{ext}", bbox_inches="tight")
    with open(f"{ruta_sin_ext}.pie.md", "w", encoding="utf-8") as f:
        f.write(pie)
    plt.close(fig)