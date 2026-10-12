# -*- coding: utf-8 -*-
"""Nomenclatura de presentación (idea 3, aprobada por el usuario el 2026-10-12).

Todo se numera como los capítulos de un informe: PREGUNTA (1–6, más el anexo A) → ESTUDIO
(2.4) → PARTE (2.4a) cuando un estudio tiene partes con datos fijos distintos. La parte
reemplaza al "bloque". Tablas y figuras siguen el número del estudio: Tabla 4.1-1, Figura 3.2-2.
Los códigos internos (KF-M05-3, B09-3, TAB-M05-00…) quedan solo como "código de origen".
"""
import re

PREGUNTA = {"1": "¿Funciona el ciclo con los datos del profesor?",
            "2": "¿Qué es lo mínimo que hay que cambiar para que funcione?",
            "3": "¿Qué variables importan y cuánto?",
            "4": "¿Qué datos del profesor se pueden conservar?",
            "5": "¿Cuánta eficiencia se puede lograr?",
            "6": "¿Son confiables los resultados?",
            "A": "Anexo: equipos fuera del rango realista (no entra en las conclusiones)"}

# caso de origen → (estudio, nombre del estudio)
ESTUDIO = {"KF-M01": ("1.1", "Repetir el caso del profesor"),
           "KF-M02-N1": ("2.1", "Un solo cambio"),
           "KF-M02-N2": ("2.2", "Dos cambios"),
           "KF-M02R": ("2.3", "Dos cambios con η y ε en 0.40–0.95"),
           "KF-M02S": ("2.4", "Sumidero más frío"),
           "KF-M03": ("3.1", "Sensibilidad local alrededor de A*"),
           "KF-M04": ("3.2", "Sensibilidad global (500 puntos)"),
           "KF-M04b": ("3.2", "Sensibilidad global (500 puntos)"),
           "KF-M04c": ("3.3", "P_baja alta (1500–2500 kPa)"),
           "KF-M05": ("4.1", "Escenarios de conservación"),
           "KF-M05c": ("4.2", "Mapa con las presiones del profesor"),
           "KF-M09": ("4.3", "Escalera de conservación"),
           "KF-M07": ("5.1", "Búsqueda de la η máxima"),
           "KF-M06": ("6.1", "Verificación con el motor de referencia"),
           "KF-M10": ("6.2", "Planta real de Húsavík"),
           "KF-M10b": ("6.2", "Planta real de Húsavík"),
           "KF-M08": ("A.1", "Equipos fuera del rango realista")}

# subcaso de origen → (parte, nombre de la parte)
_P = {"KF-M01-base": ("1.1a", "punto del profesor"), "KF-M01-P_alta": ("1.1b", "solo P_alta"),
      "KF-M01-x_b": ("1.1c", "solo x_b"), "KF-M01-T_amb": ("1.1d", "temperatura ambiente hora a hora"),
      "KF-M02-N1": ("2.1", "una variable a la vez"),
      "KF-M02-N2-A": ("2.2a", "conservar la fuente (ε_HRVG × P_baja)"),
      "KF-M02-N2-B": ("2.2b", "bajar la fuente (T_fuente × P_baja)"),
      "KF-M02R-n1": ("2.3a", "un cambio"), "KF-M02R-n2a": ("2.3b", "ε_HRVG × ε_cond"),
      "KF-M02R-n2b": ("2.3c", "ε_HRVG × P_baja"), "KF-M02R-n3": ("2.3d", "T_fuente × ε_cond"),
      "KF-M02S-B1": ("2.4a", "fuente a 403 K"), "KF-M02S-B2": ("2.4b", "fuente a 420 K"),
      "KF-M02S-B3": ("2.4c", "ε_HRVG = 0.40 (fuente del profesor)"),
      "KF-M02S-B4": ("2.4d", "datos exactos del profesor"),
      "KF-M03": ("3.1", "alrededor de A*"),
      "KF-M04": ("3.2", "muestra de 300 puntos"), "KF-M04b": ("3.2", "muestra de 200 puntos"),
      "KF-M04c": ("3.3", "P_baja de 1500 a 2500 kPa"),
      "KF-M05-1": ("4.1a", "conserva sus temperaturas"), "KF-M05-2": ("4.1b", "conserva sus presiones"),
      "KF-M05-3": ("4.1c", "conserva sus presiones y su clima"),
      "KF-M05-4": ("4.1d", "conserva su P_alta y sus temperaturas"),
      "KF-M05-5": ("4.1e", "conserva su fuente y su x_b"),
      "KF-M05c": ("4.2", "presiones del profesor, malla T_fuente × ε_cond × clima"),
      "KF-M07-A1": ("5.1a", "libre, desde el mejor de 3.2"), "KF-M07-A2": ("5.1b", "libre, desde el mejor de 2.4"),
      "KF-M07-A3": ("5.1c", "conserva sus temperaturas"),
      "KF-M07-A4": ("5.1d", "conserva sus presiones y su clima"),
      "KF-M07-A5": ("5.1e", "conserva su fuente y su x_b"),
      "KF-M06-VER": ("6.1a", "teqp frente al motor real"),
      "KF-M06-PISO": ("6.1b", "piso de cavitación a 30.4 °C"),
      "KF-M06-SUB": ("6.1c", "costo de exigir subenfriamiento"),
      "KF-M09-REAL": ("6.1d", "motor real con 1500 s"),
      "KF-M10-F3": ("6.2a", "Fase 3 de septiembre"), "KF-M10-OFAT": ("6.2b", "una variable a la vez"),
      "KF-M10-MALLA": ("6.2c", "malla x_b × P_baja (x_b 0.70–0.91)"),
      "KF-M10b-MALLA": ("6.2c", "malla x_b × P_baja (x_b 0.30–0.70)"),
      "KF-M10b-OFAT": ("6.2d", "x_b bajo (0.30–0.70)"),
      "KF-M09-HUS": ("6.2e", "P_baja mínima con su piso de diseño"),
      "KF-M08": ("A.1", "η y ε de 0.20 a 0.99")}

_B = {"B01": "1.1", "B02": "2.1", "B03-A": "2.2a", "B03-B": "2.2b", "B04-n1": "2.3a",
      "B04-n2a": "2.3b", "B04-n2b": "2.3c", "B04-n3": "2.3d", "B05-B1": "2.4a", "B05-B2": "2.4b",
      "B05-B3": "2.4c", "B05-B4": "2.4d", "B06": "3.1", "B07": "3.2", "B08": "3.3",
      "B09-1": "4.1a", "B09-2": "4.1b", "B09-3": "4.1c", "B09-4": "4.1d", "B09-5": "4.1e",
      "B10": "4.2", "B11-A1": "5.1a", "B11-A2": "5.1b", "B11-A3": "5.1c", "B11-A4": "5.1d",
      "B11-A5": "5.1e", "B12": "6.1", "B13-HUS": "6.2e", "B14-F3": "6.2a", "B14-OFAT": "6.2b",
      "B14-MALLA": "6.2c", "B14-OFATb": "6.2d", "BX": "A.1",
      "B03": "2.2", "B04": "2.3", "B05": "2.4", "B09": "4.1", "B11": "5.1", "B13": "4.3", "B14": "6.2"}

FIG = {"FIG-G01": "S-1", "FIG-G02": "S-2", "FIG-M02-01": "2.1-1", "FIG-M02-02a": "2.2-1",
       "FIG-M02-02b": "2.2-2", "FIG-M02R-n1": "2.3-1", "FIG-M02R-n2a": "2.3-2", "FIG-M02R-n2b": "2.3-3",
       "FIG-M02R-n3": "2.3-4", "FIG-M02S-01": "2.4-1", "FIG-M03-01": "3.1-1", "FIG-M03-02": "3.1-2",
       "FIG-M03-03": "3.1-3", "FIG-M03-04": "3.1-4", "FIG-M04-01": "3.2-1", "FIG-M04-02": "3.2-2",
       "FIG-M04-03": "3.2-3", "FIG-M04-04": "3.2-4", "FIG-M04c-01": "3.3-1", "FIG-M05-S1": "4.1-1",
       "FIG-M05-S2": "4.1-2", "FIG-M05-S3": "4.1-3", "FIG-M05-S4": "4.1-4", "FIG-M05-S5": "4.1-5",
       "FIG-M05c-01": "4.2-1", "FIG-M09-01": "4.3-1", "FIG-M07-01": "5.1-1", "FIG-M06-01": "6.1-1",
       "FIG-M10-01": "6.2-1", "FIG-M10-02": "6.2-2"}

# tablas: (prefijo de origen) → (estudio, desplazamiento). TAB-<mnn>-<kk> → <estudio>-<kk + 1 + desp>
_T = {"M01": ("1.1", 0), "M02-N1": ("2.1", 0), "M02-N2": ("2.2", 0), "M02R": ("2.3", 0),
      "M02S": ("2.4", 0), "M03": ("3.1", 0), "M04": ("3.2", 0), "M04c": ("3.3", 0), "M05": ("4.1", 0),
      "M05c": ("4.2", 0), "M09": ("4.3", 0), "M07": ("5.1", 0), "M06": ("6.1", 0), "M10": ("6.2", 0),
      "M10b": ("6.2", 2)}       # TAB-M10b-02 → 6.2-5 (M10b-00/01 se juntan con las de M10)


def estudio(caso):
    return ESTUDIO.get(caso, (caso, ""))[0]


def parte(subcaso):
    """(código de parte, nombre) de un subcaso de origen."""
    if subcaso in _P:
        return _P[subcaso]
    m = re.match(r"KF-M09-R(\d)-(.+)", str(subcaso))
    if m:
        return f"4.3 {m.group(2)}", f"ronda {m.group(1)}"
    return subcaso, ""


def etiqueta(subcaso):
    """Texto para tablas y listas: '4.1c · conserva sus presiones y su clima'."""
    p, n = parte(subcaso)
    return f"{p} · {n}" if n else p


def bloque(b):
    """Código de parte de un bloque de origen (B09-3 → 4.1c; B13-x_b+P_alta → 4.3 x_b+P_alta)."""
    if b in _B:
        return _B[b]
    if str(b).startswith("B13-"):
        return "4.3 " + str(b)[4:]
    return b


def tabla(t):
    """TAB-M05-00 → '4.1-1'; TAB-G03 → 'S-3'."""
    m = re.match(r"TAB-G0?(\d+)$", t)
    if m:
        return f"S-{m.group(1)}"
    m = re.match(r"TAB-(.+)-(\d\d)$", t)
    if m and m.group(1) in _T:
        e, d = _T[m.group(1)]
        return f"{e}-{int(m.group(2)) + 1 + d}"
    return t


def figura(f):
    """FIG-M04-02 (o su nombre de archivo) → '3.2-2'."""
    for k in sorted(FIG, key=len, reverse=True):
        if str(f).startswith(k):
            return FIG[k]
    return f


def nombre_figura(viejo):
    """'FIG-M04-02_plano_presiones' → ('3.2', 'Figura_3.2-2_plano_presiones')."""
    for k in sorted(FIG, key=len, reverse=True):
        if viejo.startswith(k):
            n = FIG[k]
            return n.split("-")[0], f"Figura_{n}{viejo[len(k):]}"
    return "otras", viejo


def etiqueta_bloque(b):
    """Texto de la lista del Tablero: '3.2 · Sensibilidad global (500 puntos)'. Siempre lleva letras,
    para que Excel no convierta '3.2' en número (o en fecha) y la búsqueda no falle."""
    p = bloque(b)
    if p.startswith("4.3 "):
        return p + " · escalera de conservación"
    nombre = next((n for c, (e, n) in ESTUDIO.items() if e == p), None)
    if nombre is None:
        nombre = next((n for s, (q, n) in _P.items() if q == p), "")
    return f"{p} · {nombre}"
