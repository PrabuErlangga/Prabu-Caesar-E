#!/usr/bin/env python3
"""
Generate PDF report using ReportLab (Platypus) - improved:
 - smaller logo in header
 - table column widths calculated from available page width
 - long text values wrapped using Paragraph (avoid stretching)
 - header (kop surat) with separator line and print date
 - footer with page number
"""

import sqlite3
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.units import mm
import datetime

# ----- CONFIG -----
DB_PATH = Path("backend/mahasiswa.db")         # sesuaikan jika perlu
OUTPUT_PDF = Path("backend/report/laporan_mahasiswa_kop_fixed.pdf")
LOGO_PATH = Path("backend/report/logo_gunadarma.png")   # letakkan logo (PNG/JPG). Ganti nama file sesuai unggahan.
PAGE_SIZE = A4
LEFT_MARGIN = RIGHT_MARGIN = 20 * mm
TOP_MARGIN = 30 * mm
BOTTOM_MARGIN = 20 * mm

# Kop (header) content
KOP_LINES = [
    "UNIVERSITAS GUNADARMA",
    "FTI - INFORMATIKA",
    "Jl. KH. Noer Ali, Kalimalang Bekasi, Phone : 88860117"
]

# ----- read data from sqlite -----
def read_students(db_path):
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    cur.execute("SELECT id, nim, nama, jurusan, angkatan FROM mahasiswa ORDER BY nama")
    rows = cur.fetchall()
    conn.close()
    return rows

# ----- header / footer callbacks -----
def header(canvas, doc):
    canvas.saveState()
    page_width, page_height = PAGE_SIZE

    # draw smaller logo if exists (left side) - use 20mm
    logo_space = 0
    if LOGO_PATH.exists():
        try:
            logo_w = logo_h = 20 * mm   # smaller logo
            x = LEFT_MARGIN
            y = page_height - 20 * mm - logo_h
            canvas.drawImage(str(LOGO_PATH), x, y, width=logo_w, height=logo_h, preserveAspectRatio=True, mask='auto')
            logo_space = logo_w + 6 * mm
        except Exception:
            logo_space = 0

    # central kop text (centered)
    canvas.setFont("Helvetica-Bold", 14)
    center_x = page_width / 2.0
    y_title = page_height - 18 * mm
    canvas.drawCentredString(center_x, y_title, KOP_LINES[0])

    canvas.setFont("Helvetica", 10)
    y_second = y_title - 6 * mm
    canvas.drawCentredString(center_x, y_second, KOP_LINES[1])

    canvas.setFont("Helvetica", 8)
    y_third = y_second - 5 * mm
    canvas.drawCentredString(center_x, y_third, KOP_LINES[2])

    # tanggal di pojok kanan atas
    canvas.setFont("Helvetica", 8)
    date_str = datetime.datetime.now().strftime("%d %B %Y %H:%M:%S")
    canvas.drawRightString(page_width - RIGHT_MARGIN, page_height - 14 * mm, f"Dicetak: {date_str}")

    # horizontal separator line under kop
    line_y = y_third - 8 * mm
    canvas.setStrokeColor(colors.black)
    canvas.setLineWidth(1)
    canvas.line(LEFT_MARGIN, line_y, page_width - RIGHT_MARGIN, line_y)

    canvas.restoreState()

def footer(canvas, doc):
    canvas.saveState()
    width, height = PAGE_SIZE
    canvas.setFont("Helvetica", 8)
    page_number_text = f"Halaman {doc.page}"
    canvas.drawRightString(width - RIGHT_MARGIN, 12 * mm, page_number_text)
    canvas.restoreState()

# ----- build document -----
def build_pdf(db_path, output_pdf):
    students = read_students(db_path)

    page_width, _ = PAGE_SIZE
    available_width = page_width - LEFT_MARGIN - RIGHT_MARGIN

    # define column width percentages (sum must be 1.0)
    # ID small, NIM small, Nama large, Jurusan medium, Angkatan small
    col_percents = [0.06, 0.16, 0.42, 0.24, 0.12]
    col_widths = [available_width * p for p in col_percents]

    doc = SimpleDocTemplate(
        str(output_pdf),
        pagesize=PAGE_SIZE,
        leftMargin=LEFT_MARGIN, rightMargin=RIGHT_MARGIN,
        topMargin=TOP_MARGIN, bottomMargin=BOTTOM_MARGIN
    )

    styles = getSampleStyleSheet()
    normal = styles["BodyText"]
    # reduce font size slightly for table body to fit better
    body_style = ParagraphStyle("table_body", parent=normal, fontSize=9, leading=11)
    title_style = styles["Title"]
    title_style.fontSize = 14
    title_style.alignment = 1  # center

    elements = []
    elements.append(Spacer(1, 6 * mm))
    elements.append(Paragraph("DATA MAHASISWA", title_style))
    elements.append(Spacer(1, 6 * mm))

    # prepare table data with Paragraphs to enable wrapping
    header_row = ["ID", "NIM", "Nama", "Jurusan", "Angkatan"]
    data = [header_row]

    for r in students:
        id_cell = Paragraph(str(r[0]), body_style)
        nim_cell = Paragraph(r[1] or "", body_style)
        nama_cell = Paragraph(r[2] or "", body_style)
        jurusan_cell = Paragraph(r[3] or "", body_style)
        angkatan_cell = Paragraph(str(r[4]) if r[4] is not None else "", body_style)
        data.append([id_cell, nim_cell, nama_cell, jurusan_cell, angkatan_cell])

    # Create table with calculated column widths, repeat header each page
    table = Table(data, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f0f0f0")),
        ('TEXTCOLOR',(0,0),(-1,0),colors.black),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.35, colors.grey),
        ('LEFTPADDING',(0,0),(-1,-1),4),
        ('RIGHTPADDING',(0,0),(-1,-1),4),
    ]))

    elements.append(table)
    elements.append(Spacer(1,6 * mm))
    elements.append(Paragraph("Catatan: Laporan generated via ReportLab", normal))

    doc.build(elements, onFirstPage=lambda c,d: (header(c,d), footer(c,d)),
                    onLaterPages=lambda c,d: (header(c,d), footer(c,d)))
    print("PDF created at:", output_pdf)

if __name__ == "__main__":
    OUTPUT_PDF.parent.mkdir(parents=True, exist_ok=True)
    if not DB_PATH.exists():
        print("DB not found at", DB_PATH, "— ubah DB_PATH di script jika diperlukan.")
    else:
        build_pdf(DB_PATH, OUTPUT_PDF)
