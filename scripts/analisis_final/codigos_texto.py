# -*- coding: utf-8 -*-
"""Traduce a la nomenclatura nueva (codigos.py) cualquier texto con códigos viejos: pies, títulos,
encabezados, fichas e informes. No toca rutas ni nombres de archivo de origen (REPORTE_M3.md,
final_M5/, m3_ofat.csv): un código solo se cambia si no va pegado a '_', '/', '.' ni a una letra."""
import re

import codigos as C

_NO_ANTES, _NO_DESPUES = r"(?<![\w/.\-])", r"(?![\w\-])"

# Prosa: formas cortas usadas en fichas, informes y conclusiones (las más largas primero).
_PROSA = {"M4/M4b": "estudio 3.2", "M4 + M4b": "estudio 3.2", "M04 + M04b": "estudio 3.2",
          "M10/M10b": "estudio 6.2", "M10 + M10b": "estudio 6.2",
          "M2-N1": "estudio 2.1", "M2-N2": "estudio 2.2", "M02-N1": "estudio 2.1", "M02-N2": "estudio 2.2",
          "M2R": "estudio 2.3", "M02R": "estudio 2.3", "M2S": "estudio 2.4", "M02S": "estudio 2.4",
          "M4b": "estudio 3.2", "M04b": "estudio 3.2", "M4c": "estudio 3.3", "M04c": "estudio 3.3",
          "M5c": "estudio 4.2", "M05c": "estudio 4.2", "M10b": "estudio 6.2",
          "M01": "estudio 1.1", "M1": "estudio 1.1", "M02": "estudios 2.1 y 2.2", "M2": "estudios 2.1 y 2.2",
          "M03": "estudio 3.1", "M3": "estudio 3.1", "M04": "estudio 3.2", "M4": "estudio 3.2",
          "M05": "estudio 4.1", "M5": "estudio 4.1", "M06": "estudio 6.1", "M6": "estudio 6.1",
          "M07": "estudio 5.1", "M7": "estudio 5.1", "M08": "anexo A.1", "M8": "anexo A.1",
          "M09": "estudio 4.3", "M9": "estudio 4.3", "M10": "estudio 6.2"}
for _k in range(1, 6):
    _PROSA[f"M5-S{_k}"] = f"estudio 4.1{'abcde'[_k - 1]}"
    _PROSA[f"M7-A{_k}"] = f"estudio 5.1{'abcde'[_k - 1]}"
for _k in range(1, 5):
    _PROSA[f"M2S-B{_k}"] = f"estudio 2.4{'abcd'[_k - 1]}"


def _rx(clave):
    return re.compile(_NO_ANTES + re.escape(clave) + _NO_DESPUES)


def _ruta_figura(m):
    est, nombre = C.nombre_figura(m.group(1))
    return f"03_figuras/{est}/{nombre}"


def traducir(texto):
    if not isinstance(texto, str) or not texto:
        return texto
    t = texto.replace("M1–M10b", "campaña final").replace("campaña campaña final", "campaña final")
    t = re.sub(r"03_figuras/[^/\s)]+/(FIG-[^)\s]+)", _ruta_figura, t)          # enlaces a figuras
    t = re.sub(r"(?:Figura )?(FIG-(?:G0\d|M[0-9A-Za-z\-]+?))(?=[_.\s,;:)\]]|$)",
               lambda m: "Figura " + C.figura(m.group(1)), t)
    t = re.sub(r"(?:Tabla )?TAB-(G0\d|M[0-9A-Za-z\-]+?-\d\d)(?![\w])",
               lambda m: "Tabla " + C.tabla("TAB-" + m.group(1)), t)
    t = re.sub(r"FICHA_KF-([\w-]+?)(?:\.md)?(?![\w-])", lambda m: "Ficha " + C.estudio("KF-" + m.group(1).split("_")[0]), t)
    t = re.sub(_NO_ANTES + r"KF-M09-R(\d)-([\w+]+)", lambda m: f"4.3 ronda {m.group(1)}: {m.group(2)}", t)
    t = re.sub(r"KF-M04 \+ KF-M04b|KF-M10 \+ KF-M10b", lambda m: "estudio " + C.estudio(m.group(0)[:6]), t)
    for k in sorted(C._P, key=len, reverse=True):                            # subcasos → partes
        if "-" in k[3:] or k in ("KF-M02-N1", "KF-M08"):
            t = _rx(k).sub(C.parte(k)[0], t)
    for k in sorted(C.ESTUDIO, key=len, reverse=True):                      # casos → estudios
        t = _rx(k).sub("estudio " + C.estudio(k), t)
    t = re.sub(_NO_ANTES + r"B13-([\w+]+)", lambda m: "parte " + C.bloque(m.group(0)), t)
    for k in sorted(C._B, key=len, reverse=True):                           # bloques → partes
        n = C.bloque(k)
        t = _rx(k).sub(("parte " if n[-1].isalpha() else "estudio ") + n, t)
    for k in sorted(_PROSA, key=len, reverse=True):
        t = _rx(k).sub(_PROSA[k], t)
    # limpieza de dobles palabras que deja la sustitución
    for a, b in (("Bloques estudio", "Estudio"), ("Bloque estudio", "Estudio"), ("Bloque parte", "Parte"),
                 ("bloque estudio", "estudio"), ("bloque parte", "parte"), ("bloques estudio", "estudios"),
                 ("caso estudio", "estudio"), ("Caso estudio", "Estudio"), ("estudio estudio", "estudio"),
                 ("casos estudio", "estudios"), ("del estudio estudio", "del estudio"), ("Ficha Ficha", "Ficha"),
                 ("Figura Figura", "Figura"), ("Tabla Tabla", "Tabla"), ("bloques **parte", "partes **"),
                 ("bloque **parte", "parte **"), ("bloque **estudio", "estudio **"),
                 ("Bloque(s): parte", "Parte(s):"), ("Bloque(s): estudio", "Estudio:")):
        t = t.replace(a, b)
    return _sin_repetir(t)


def _sin_repetir(t):
    """Quita repeticiones que aparecen al juntar casos (3.2 = M4 + M4b; 6.2c = dos mallas)."""
    t = re.sub(r"(estudios? [\dA.]+[a-e]?)(?:, \1)+", r"\1", t)
    t = re.sub(r"(\d\.\d[a-e]?)(?: \+ \1)+", r"\1", t)
    t = re.sub(r"(estudio ([\dA.]+)) \((?:estudio|parte) \2\)", r"\1", t)
    lineas = []
    for linea in t.split("\n"):
        seg, vistos = [], set()
        for s in linea.split(" · "):
            clave = re.sub(r"^(estudio|parte) ", "", s.strip().lower())
            if clave and clave in vistos:
                continue
            vistos.add(clave)
            seg.append(s)
        lineas.append(" · ".join(seg))
    return "\n".join(lineas)
