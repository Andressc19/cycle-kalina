# -*- coding: utf-8 -*-
"""Sens2 - s2_informe_pdf: informe tecnico con figuras (HTML + PDF por Edge headless) desde los CSV y las conclusiones."""
import base64
import html
import os
import subprocess
import sys

import pandas as pd

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
sys.path.insert(0, AQUI)
from s2_cargar import conclusiones  # noqa: E402

FIG = os.path.join(RAIZ, "docs", "figuras_sens2")
HTML = os.path.join(RAIZ, "docs", "INFORME_TECNICO_SENS2.html")
PDF = os.path.join(RAIZ, "docs", "INFORME_TECNICO_SENS2.pdf")
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
U1 = os.path.join(RAIZ, "resultados", "2026-10-17_sens2_U1")
CSS = """body{font-family:Georgia,serif;font-size:10.5pt;line-height:1.38;margin:0 6mm;color:#111}
h1{font-size:19pt;margin:0 0 4pt}h2{font-size:14pt;border-bottom:1.5px solid #1F4E79;color:#1F4E79;margin-top:18pt}
h3{font-size:11.5pt;margin:12pt 0 3pt}table{border-collapse:collapse;margin:6pt 0;font-size:9pt}
td,th{border:1px solid #999;padding:2px 5px;text-align:left;vertical-align:top}th{background:#DDEBF7}
figure{margin:8pt 0;page-break-inside:avoid}img{max-width:100%}figcaption{font-size:9pt;color:#333}
.c{margin:5pt 0;padding:4pt 7pt;border-left:3px solid #1F4E79;background:#F5F8FC;page-break-inside:avoid}
.d{font-size:9pt;color:#222}.n{font-size:9pt;font-style:italic}"""


def img(nombre, pie):
    with open(os.path.join(FIG, nombre), "rb") as fh:
        b = base64.b64encode(fh.read()).decode()
    return '<figure><img src="data:image/png;base64,%s"><figcaption><b>Figura.</b> %s</figcaption></figure>' % (b, html.escape(pie))


def parrafos(c, ids):
    out = []
    for i in ids:
        r = c[c["id"] == i].iloc[0]
        out.append('<div class="c"><b>%s</b> [%s, fase %s, confianza %s]. %s<div class="d"><b>Evidencia:</b> %s<br><b>Implicación:</b> %s</div></div>'
                   % (i, html.escape(r["categoria"]), r["fase"], r["confianza"], html.escape(r["afirmacion"]),
                      html.escape(r["evidencia"]), html.escape(r["implicacion"])))
    return "".join(out)


def tabla_u1():
    f = os.path.join(U1, "u1_resumen.csv")
    if not os.path.exists(f):
        return ""
    r = pd.read_csv(f)
    nombre = {"U1A": "A, lote 1", "U1A2": "A, lote 2", "U1Ap": "A, lotes 1+2", "U1B": "B (tolerancia ×2)",
              "U1C": "A con ε_cond fija en 0.95"}
    filas = ["<tr><th>Escenario</th><th>Bloque</th><th>n</th><th>P(KALINA)</th><th>IC 95 %</th><th>P con m_O2 ≥ 1 K</th>"
             "<th>P con m_O2 ≥ 3 K</th><th>P con m_O2 ≥ 5 K</th><th>η P5–P50–P95 (%)</th></tr>"]
    for e in ("U1A", "U1A2", "U1Ap", "U1B", "U1C"):
        for _, x in r[r["escenario"] == e].iterrows():
            filas.append("<tr><td>%s</td><td>%s</td><td>%d</td><td>%.2f</td><td>[%.2f, %.2f]</td><td>%.2f</td><td>%.2f</td><td>%.2f</td><td>%.1f–%.1f–%.1f</td></tr>"
                         % (nombre[e], x["centro"], x["n"], x["p_kalina"], x["p_lo"], x["p_hi"], x["p_m1"], x["p_m3"], x["p_m5"],
                            x["eta_p5"], x["eta_p50"], x["eta_p95"]))
    return "<table>%s</table>" % "".join(filas)


def construir():
    c = conclusiones()
    h = ["<html><head><meta charset='utf-8'><title>Informe técnico de Sensibilidad 2</title><style>%s</style></head><body>" % CSS]
    h.append("<h1>Análisis de sensibilidad del ciclo Kalina KSC-11 (NH₃–H₂O)</h1><p class='n'>Informe técnico de la campaña «Sensibilidad 2»: "
             "análisis de 3 921 puntos de Sensibilidad 1 y de 384 + 424 puntos nuevos de propagación de incertidumbre. Rama "
             "<code>test/anal_terremoto</code>. Todo número sale de los CSV de <code>resultados/</code>; libro de apoyo "
             "<code>datos/Kalina_anal_sensible_2.xlsx</code>.</p>")
    h.append("<h2>1. Resumen</h2><ul><li>La región KALINA depende del bloque y del lado frío del ciclo (los barridos de una variable la hallan con fuentes de 90 a 165 °C en C1, 120 a 190 °C en C2, 90 a 290 °C en C3 y 90 a 250 °C en C4): "
             "el piso de P_baja (cavitación), la efectividad del condensador y x_b.</li>"
             "<li>La eficiencia máxima es 14.53 % dentro del rango experimental y 14.82 % fuera (fuente de 170 °C).</li>"
             "<li>El regenerador pierde peso al subir la temperatura de la fuente.</li>"
             "<li>Los resultados valen para margen de cavitación cero; con 3 K de margen la región KALINA se reduce de forma importante (sección 6).</li>"
             "<li>Solo se usó el motor teqp: no hay validación experimental propia del ciclo.</li></ul>")
    h.append("<h2>2. Preguntas del profesor y dónde se responden</h2><table><tr><th>Pregunta</th><th>Sección</th></tr>"
             "<tr><td>1. Rangos donde hay Kalinas</td><td>4.1</td></tr><tr><td>2. Partir de un KALINA y mover una, dos o más variables</td><td>4.2</td></tr>"
             "<tr><td>3. Comportamiento del regenerador y del ciclo en un rango de temperaturas</td><td>4.4</td></tr>"
             "<tr><td>4. Datos para preseleccionar equipos</td><td>4.5</td></tr></table>")
    h.append("<h2>3. Datos y método</h2><p>Campaña Sensibilidad 1: 3 921 puntos en cuatro centros KALINA (C1 Húsavík, C2 ancla A*, C3 caliente 150 °C, C4 frío 110 °C) con "
             "barridos de una variable, mallas de pares 7×7 y muestreo LHS de 9 variables; 3 663 sin duplicados exactos. Clase KALINA: se cumplen los criterios "
             "O1 (título de salida q4 ≥ 0.90), O2 (m_O2 = T_burbuja(P_baja, x_b) − T9 ≥ 0, <b>margen cero</b>), O3 (W_net &gt; 0) y O5 (mezcla bifásica en el separador). "
             "Índices globales sobre el LHS de cada bloque con tres variables dummy como piso de ruido, bootstrap y, para F1 a F3, 2 000 permutaciones con corrección de Benjamini–Hochberg; superficies de respuesta sobre las mallas de pares; propagación de "
             "incertidumbre con LHS de las 10 variables alrededor de cada centro (tolerancias uniformes supuestas: T_fuente ±5 K, T_sumidero ±3 K, P ±5 %, x_b ±0.02, "
             "η y ε ±0.05; escenario B el doble). Eficiencias y efectividades en [0.40, 0.95]; T_sumidero de 5 a 30 °C igual a la temperatura ambiente de diseño; m_b = 1.</p>")
    h.append("<h2>4. Resultados</h2><h3>4.1 Dónde existe KALINA</h3>" + parrafos(c, ["D1", "D2", "D3", "D4", "D5", "D6", "D8"]))
    h.append(img("f1_piso_pbaja.png", "Piso de P_baja (menor P_baja con KALINA) en cada columna de x_b de las mallas P_baja × x_b."))
    h.append("<h3>4.2 Qué pasa al mover variables desde un KALINA</h3>" + parrafos(c, ["D7", "L6", "U1", "U4", "U2", "U3"]))
    h.append(tabla_u1())
    if os.path.exists(os.path.join(FIG, "f7_incertidumbre.png")):
        h.append(img("f7_incertidumbre.png", "Probabilidad de seguir siendo KALINA al perturbar las 10 variables a la vez."))
    if os.path.exists(os.path.join(FIG, "f8_scan_epscond.png")):
        h.append(img("f8_scan_epscond.png", "Barrido fino de ε_cond: m_O2 cruza cero cerca de 0.92 en C1 y de 0.905 en C4; C2 y C3 no lo cruzan."))
    h.append(img("f4_margenes.png", "Margen de operación desde el centro, una variable cada vez (C1 y C4)."))
    h.append("<h3>4.3 CORREGIBLE frente a KALINA</h3>" + parrafos(c, ["F6", "L1", "L2", "L3"]))
    h.append(img("f5_corregibles.png", "η mediana de KALINA y CORREGIBLE por bloque."))
    h.append("<h3>4.4 Regenerador frente a la temperatura de la fuente</h3>" + parrafos(c, ["E8", "E4"]))
    h.append(img("f3_regenerador.png", "Q_reg/Q_i de los KALINA en los barridos de T_fuente de una variable."))
    h.append("<h3>4.5 Datos para preseleccionar equipos</h3>" + parrafos(c, ["E1", "E2", "E3", "E5", "E6", "E7"]))
    h.append("<h3>4.6 Eficiencia, sensibilidad e interacciones</h3>" + parrafos(c, ["M1", "M2", "M3", "M4", "M5", "R1", "F1", "F2", "F3", "F4", "F5"]))
    h.append(img("f2_eta_pbaja.png", "η frente a P_baja por nivel de x_b; cada curva empieza donde empieza la región KALINA."))
    h.append("<h2>5. Contraste con la literatura</h2><table><tr><th>Fuente</th><th>Dato de la fuente</th><th>Este trabajo</th><th>Lectura</th></tr>"
             "<tr><td>Planta de Húsavík (informe GRC 2002, texto leído)</td><td>Salmuera de 121 °C (90 kg/s, enfriada a 80 °C); mezcla 82 % NH₃; líquido saturado a la "
             "salida del condensador a 5.4 bar-a y 12.4 °C; potencia neta medida 1 696 y 1 719 kW.</td><td>C1: fuente de 121 °C, x_b 0.82; η del centro 12.0 %; "
             "primer P_baja con KALINA 600 kPa con sumidero de 5 °C.</td><td>x_b y temperatura coinciden. η real estimada ≈ 10.9 % (1 696 kW / (90 kg/s · 4.2 kJ/kg·K · 41 K), "
             "suponiendo cp del agua; la fuente no lo declara): el modelo da 1.1 puntos más, coherente con la banda de ±0.7 pp del modelo de propiedades más auxiliares y pérdidas no "
             "modeladas. La planta real opera con líquido saturado antes de la bomba, es decir, margen termodinámico cero; la fuente no describe cómo se asegura el NPSH.</td></tr>"
             "<tr><td>Elsayed et al. 2013 (PDF local)</td><td>Fracción de amoníaco recomendada entre 0.55 y 0.9.</td><td>Ventana de existencia de x_b en C1: de 0.525 a 0.925.</td>"
             "<td>Coinciden.</td></tr><tr><td>Verificación propia del proyecto</td><td>Benchmark contra Elsayed/Embaye (23 puntos, |Δη| medio 0.27 pp) y banda de η del "
             "modelo de propiedades de ±0.4 a ±0.7 pp.</td><td>—</td><td>Es contraste con modelos publicados, no validación experimental.</td></tr></table>"
             "<p class='n'>No se usó la cifra de 11.7 % de Jailolo: su fuente no se pudo abrir (error de conexión).</p>")
    h.append("<h2>6. Amenazas a la validez</h2>" + parrafos(c, ["L7", "L4", "L5"]))
    h.append(img("f6_margen_o2.png", "Distribución del margen de cavitación m_O2 de los KALINA."))
    h.append("<h2>7. Conclusiones restantes</h2>" + parrafos(c, [i for i in c["id"] if i not in set(
        ["D1", "D2", "D3", "D4", "D5", "D6", "D8", "D7", "L6", "U1", "U2", "U3", "F6", "L1", "L2", "L3", "E8", "E4", "E1", "E2", "E3", "E5", "E6", "E7",
         "M1", "M2", "M3", "M4", "M5", "R1", "F1", "F2", "F3", "F4", "F5", "L7", "L4", "L5"])]))
    h.append("<h2>8. Trabajo futuro</h2><ol><li>Validar con el motor real los 7 puntos atípicos y los óptimos.</li><li>Repetir la propagación con tolerancias medidas o acordadas "
             "y con más de 200 puntos por celda.</li><li>Explicar con un balance termodinámico por qué el regenerador pierde peso al subir T_fuente.</li>"
             "<li>Contrastar con más plantas reales cuando se consigan sus datos.</li></ol>")
    h.append("<h2>Anexo. Reproducibilidad</h2><p>Scripts en <code>scripts/sens2/</code> (p1–p4, u1, s2_*), semilla 20261017, motor teqp, intérprete del proyecto. "
             "Informe de validación: <code>docs/VALIDACION_SENS2.md</code>.</p></body></html>")
    with open(HTML, "w", encoding="utf-8") as fh:
        fh.write("".join(h))
    subprocess.run([EDGE, "--headless", "--disable-gpu", "--no-pdf-header-footer", "--print-to-pdf=" + PDF, "file:///" + HTML.replace("\\", "/")],
                   check=False, timeout=180, capture_output=True)
    print("OK:", HTML, os.path.exists(PDF) and os.path.getsize(PDF))


if __name__ == "__main__":
    construir()
