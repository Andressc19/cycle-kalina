# -*- coding: utf-8 -*-
"""Post-procesa el .docx generado por pandoc (entregable1_kalina_tercero.md)
para que cumpla la estructura APA7 (estudiante): portada, márgenes, fuente,
interlineado, sangrías, títulos, referencias con sangría francesa, numeración
de página y tablas sin bordes verticales.
"""
import copy
import docx
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

SRC = "cuerpo_pandoc.docx"
OUT = "KALINAKCS11.docx"

FUENTE = "Times New Roman"
TAMANO = Pt(12)

TITULO = "Análisis de sensibilidad del ciclo Kalina KCS11"
SUBTITULO = "Entregable 1 — Introducción, descripción del ciclo y formulación"
AUTORES = ["Jose Duran", "Julian Gómez Mora", "Javier Villamizar",
           "Andrés Laguado", "Felipe Diaz"]
AFILIACION = ("Departamento de Ingeniería Mecánica, "
              "Universidad Francisco de Paula Santander")
CURSO = "Motores y Turbinas"
DOCENTE = "Ing. Faustino Moreno"
FECHA = "22 de septiembre de 2026"

HEADINGS_1_ALL_CAPS = True  # convención ya usada/aceptada en el entregable anterior del curso


def set_run_font(run):
    run.font.name = FUENTE
    run.font.size = TAMANO
    run.font.color.rgb = RGBColor(0, 0, 0)
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn('w:rFonts'))
    if rFonts is None:
        rFonts = OxmlElement('w:rFonts')
        rPr.append(rFonts)
    for attr in ('w:ascii', 'w:hAnsi', 'w:cs', 'w:eastAsia'):
        rFonts.set(qn(attr), FUENTE)
    # quita cualquier color de tema heredado del estilo (el azul de Heading 1/2/3 de Word)
    color_el = rPr.find(qn('w:color'))
    if color_el is not None:
        for attr in ('w:themeColor', 'w:themeTint', 'w:themeShade'):
            if color_el.get(qn(attr)) is not None:
                del color_el.attrib[qn(attr)]
        color_el.set(qn('w:val'), '000000')


def set_paragraph_format(p, first_line_indent=None, alignment=None,
                          left_indent=None, hanging=None, bold=None,
                          italic=None, keep_size=None):
    pf = p.paragraph_format
    pf.line_spacing_rule = WD_LINE_SPACING.DOUBLE
    pf.space_before = Pt(0)
    pf.space_after = Pt(0)
    if alignment is not None:
        pf.alignment = alignment
    if first_line_indent is not None:
        pf.first_line_indent = first_line_indent
    if left_indent is not None:
        pf.left_indent = left_indent
    if hanging is not None:
        pf.first_line_indent = -hanging
        pf.left_indent = hanging
    if not p.runs:
        return
    for r in p.runs:
        set_run_font(r)
        if bold is not None:
            r.bold = bold
        if italic is not None:
            r.italic = italic
        if keep_size is not None:
            r.font.size = keep_size


def add_page_number_field(paragraph):
    run = paragraph.add_run()
    fld1 = OxmlElement('w:fldChar')
    fld1.set(qn('w:fldCharType'), 'begin')
    instr = OxmlElement('w:instrText')
    instr.set(qn('xml:space'), 'preserve')
    instr.text = 'PAGE'
    fld2 = OxmlElement('w:fldChar')
    fld2.set(qn('w:fldCharType'), 'end')
    run._r.append(fld1)
    run._r.append(instr)
    run._r.append(fld2)
    set_run_font(run)


def strip_table_vertical_borders(table):
    tbl = table._tbl
    tblPr = tbl.tblPr
    borders = tblPr.find(qn('w:tblBorders'))
    if borders is None:
        borders = OxmlElement('w:tblBorders')
        tblPr.append(borders)
    else:
        for child in list(borders):
            borders.remove(child)
    for edge in ('left', 'right', 'insideV'):
        el = OxmlElement(f'w:{edge}')
        el.set(qn('w:val'), 'nil')
        borders.append(el)
    for edge in ('top', 'bottom', 'insideH'):
        el = OxmlElement(f'w:{edge}')
        el.set(qn('w:val'), 'single')
        el.set(qn('w:sz'), '4')
        el.set(qn('w:space'), '0')
        el.set(qn('w:color'), '000000')
        borders.append(el)
    for row in table.rows:
        for cell in row.cells:
            for p in cell.paragraphs:
                set_paragraph_format(p, first_line_indent=Cm(0))


def build_portada(doc):
    body = doc.element.body
    first_el = body[0]

    def new_par(align=WD_ALIGN_PARAGRAPH.CENTER):
        p = doc.add_paragraph()
        p.alignment = align
        pf = p.paragraph_format
        pf.line_spacing_rule = WD_LINE_SPACING.DOUBLE
        pf.space_before = Pt(0)
        pf.space_after = Pt(0)
        return p

    # separar en un documento temporal la portada y moverla al inicio
    portada_paragraphs = []

    for _ in range(3):
        p = new_par()
        portada_paragraphs.append(p._p)

    p_titulo = new_par()
    r = p_titulo.add_run(TITULO)
    r.bold = True
    set_run_font(r)
    portada_paragraphs.append(p_titulo._p)

    p_sub = new_par()
    r = p_sub.add_run(SUBTITULO)
    set_run_font(r)
    portada_paragraphs.append(p_sub._p)

    for _ in range(2):
        p = new_par()
        portada_paragraphs.append(p._p)

    autores_txt = ", ".join(AUTORES[:-1]) + " y " + AUTORES[-1]
    p_aut = new_par()
    r = p_aut.add_run(autores_txt)
    set_run_font(r)
    portada_paragraphs.append(p_aut._p)

    p_afil = new_par()
    r = p_afil.add_run(AFILIACION)
    set_run_font(r)
    portada_paragraphs.append(p_afil._p)

    for _ in range(2):
        p = new_par()
        portada_paragraphs.append(p._p)

    for texto in (CURSO, f"Docente: {DOCENTE}", FECHA):
        p = new_par()
        r = p.add_run(texto)
        set_run_font(r)
        portada_paragraphs.append(p._p)

    # salto de página tras la portada
    p_break = doc.add_paragraph()
    p_break.paragraph_format.space_before = Pt(0)
    p_break.paragraph_format.space_after = Pt(0)
    run_break = p_break.add_run()
    run_break.add_break(docx.enum.text.WD_BREAK.PAGE)
    portada_paragraphs.append(p_break._p)

    # mover todos los párrafos de la portada (creados al final del body) al inicio
    for el in portada_paragraphs:
        body.remove(el)
    for el in portada_paragraphs:
        first_el.addprevious(el)


def insert_title_before_first_heading(doc):
    """Repite el título en negrita centrado en la primera página del cuerpo,
    justo antes del primer título de nivel 1 (NOMENCLATURA)."""
    for p in doc.paragraphs:
        if p.style.name == "Heading 1":
            new_p_el = OxmlElement('w:p')
            p._p.addprevious(new_p_el)
            from docx.text.paragraph import Paragraph
            new_p = Paragraph(new_p_el, p._parent)
            new_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            pf = new_p.paragraph_format
            pf.line_spacing_rule = WD_LINE_SPACING.DOUBLE
            pf.space_before = Pt(0)
            pf.space_after = Pt(0)
            r = new_p.add_run(TITULO)
            r.bold = True
            set_run_font(r)
            new_p.paragraph_format.page_break_before = True
            break


def force_page_break_before_sections(doc):
    """Cada sección de nivel 1 empieza en página nueva, salvo NOMENCLATURA
    (que ya queda justo debajo del título repetido en la primera página del
    cuerpo). Sustituye a los \\newpage del markdown, que pandoc descarta en
    silencio al no estar habilitada la extensión raw_tex."""
    for p in doc.paragraphs:
        if p.style.name == "Heading 1" and "NOMENCLATURA" not in p.text.upper():
            p.paragraph_format.page_break_before = True


TITULOS_TABLAS = [
    "Nomenclatura — Variables",
    "Nomenclatura — Letras griegas",
    "Nomenclatura — Subíndices",
    "Nomenclatura — Superíndices y notación auxiliar",
    "Nomenclatura — Siglas",
    "Grados de libertad según la regla de fases de Gibbs",
    "Subsistemas del ciclo Kalina KCS-11 según nivel de presión",
    "Tabla de corrientes del ciclo",
    "Especificación de los estados del ciclo",
]


def insert_table_captions(doc):
    from docx.text.paragraph import Paragraph
    body = doc.element.body
    tablas = doc.tables
    for idx, tabla in enumerate(tablas):
        titulo = TITULOS_TABLAS[idx] if idx < len(TITULOS_TABLAS) else f"Tabla {idx + 1}"
        tbl_el = tabla._tbl

        cap_titulo_el = OxmlElement('w:p')
        tbl_el.addprevious(cap_titulo_el)
        cap_titulo = Paragraph(cap_titulo_el, tabla._parent)
        cap_titulo.alignment = WD_ALIGN_PARAGRAPH.LEFT
        pf = cap_titulo.paragraph_format
        pf.line_spacing_rule = WD_LINE_SPACING.DOUBLE
        pf.space_before = Pt(0)
        pf.space_after = Pt(0)
        pf.first_line_indent = Cm(0)
        r2 = cap_titulo.add_run(titulo)
        r2.italic = True
        set_run_font(r2)

        cap_num_el = OxmlElement('w:p')
        cap_titulo_el.addprevious(cap_num_el)
        cap_num = Paragraph(cap_num_el, tabla._parent)
        cap_num.alignment = WD_ALIGN_PARAGRAPH.LEFT
        pf = cap_num.paragraph_format
        pf.line_spacing_rule = WD_LINE_SPACING.DOUBLE
        pf.space_before = Pt(0)
        pf.space_after = Pt(0)
        pf.first_line_indent = Cm(0)
        r1 = cap_num.add_run(f"Tabla {idx + 1}")
        r1.bold = True
        set_run_font(r1)


def main():
    doc = Document(SRC)

    # 1) márgenes y tamaño de página (carta, 2.54 cm)
    for section in doc.sections:
        section.top_margin = Cm(2.54)
        section.bottom_margin = Cm(2.54)
        section.left_margin = Cm(2.54)
        section.right_margin = Cm(2.54)
        section.page_width = Cm(21.59)
        section.page_height = Cm(27.94)

    # 2) estilo Normal y estilos de título: fuente, tamaño y color negro explícito
    #    (Word aplica azul por defecto a Heading 1/2/3 vía el tema; el auditor no
    #    revisa color, así que hay que forzarlo aquí y también a nivel de run).
    for style_name in ('Normal', 'Heading 1', 'Heading 2', 'Heading 3',
                        'Title', 'Subtitle'):
        try:
            st = doc.styles[style_name]
        except KeyError:
            continue
        st.font.name = FUENTE
        st.font.color.rgb = RGBColor(0, 0, 0)
        st.paragraph_format.line_spacing_rule = WD_LINE_SPACING.DOUBLE
        st.paragraph_format.space_before = Pt(0)
        st.paragraph_format.space_after = Pt(0)
    normal = doc.styles['Normal']
    normal.font.size = TAMANO

    # 3) recorrer párrafos y aplicar formato según estilo
    heading_seen = {"h1": 0}
    for p in doc.paragraphs:
        style = p.style.name
        if style == "Title" or style == "Subtitle":
            # se eliminarán: el contenido real va en la portada aparte
            for r in list(p.runs):
                r.text = ""
            continue
        if style == "Heading 1":
            set_paragraph_format(p, first_line_indent=Cm(0),
                                  alignment=WD_ALIGN_PARAGRAPH.CENTER,
                                  bold=True)
        elif style == "Heading 2":
            set_paragraph_format(p, first_line_indent=Cm(0),
                                  alignment=WD_ALIGN_PARAGRAPH.LEFT,
                                  bold=True)
        elif style == "Heading 3":
            set_paragraph_format(p, first_line_indent=Cm(0),
                                  alignment=WD_ALIGN_PARAGRAPH.LEFT,
                                  bold=True, italic=True)
        elif style in ("First Paragraph", "Body Text"):
            set_paragraph_format(p, first_line_indent=Cm(1.27),
                                  alignment=WD_ALIGN_PARAGRAPH.LEFT)
        elif style == "Compact":
            set_paragraph_format(p, first_line_indent=Cm(0),
                                  alignment=WD_ALIGN_PARAGRAPH.LEFT)
        elif style in ("Image Caption", "Caption"):
            set_paragraph_format(p, first_line_indent=Cm(0),
                                  alignment=WD_ALIGN_PARAGRAPH.CENTER)
        else:
            set_paragraph_format(p, first_line_indent=Cm(0))

    # 3b) captions "Tabla N" antes de cada tabla (requisito APA)
    insert_table_captions(doc)

    # 4) localizar la sección de Referencias, quitar el numeral del título
    #    (el auditor exige el texto exacto "Referencias") y aplicar sangría francesa
    in_refs = False
    for p in doc.paragraphs:
        if p.style.name == "Heading 1" and "REFERENCIAS" in p.text.upper():
            for r in list(p.runs):
                r.text = ""
            p.runs[0].text = "Referencias"
            in_refs = True
            continue
        if in_refs and p.text.strip():
            set_paragraph_format(p, first_line_indent=None,
                                  alignment=WD_ALIGN_PARAGRAPH.LEFT,
                                  hanging=Cm(1.27))

    # 5) tablas: sin bordes verticales, fuente correcta
    for t in doc.tables:
        strip_table_vertical_borders(t)
        for row in t.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    for r in p.runs:
                        set_run_font(r)

    # 6) numeración de página en el encabezado (derecha), desde la página 1
    section = doc.sections[0]
    header = section.header
    header.is_linked_to_previous = False
    hp = header.paragraphs[0] if header.paragraphs else header.add_paragraph()
    hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    hp.paragraph_format.space_before = Pt(0)
    hp.paragraph_format.space_after = Pt(0)
    add_page_number_field(hp)

    # 7) repetir el título en negrita al inicio del cuerpo (antes de NOMENCLATURA)
    insert_title_before_first_heading(doc)

    # 7b) salto de página real antes de cada sección de nivel 1 (2-9)
    force_page_break_before_sections(doc)

    # 8) construir la portada al inicio del documento
    build_portada(doc)

    doc.save(OUT)
    print("Guardado:", OUT)


if __name__ == "__main__":
    main()
