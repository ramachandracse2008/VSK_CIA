from fpdf import FPDF
import io
import streamlit as st

def generate_pdf(df, subject_name):
    pdf = FPDF('L', 'mm', 'A4')
    pdf.add_page()
    pdf.set_left_margin(20)
    pdf.set_font('Arial', '', 10)

    columns = df.columns.tolist()

    col_widths = {
        "S.No.": 10,
        "Regd.No.": 20,
        "Student Name": 55,
        "Assignment 1": 15,
        "Seminar/Quiz 1": 18,
        "NCC/NSS 1": 15,
        "Mid I": 12,
        "Total 1": 12,
        "Assignment 2": 15,
        "Seminar/Quiz 2": 18,
        "NCC/NSS 2": 15,
        "Mid II": 12,
        "Total 2": 12,
        "Total 1 + Total 2": 20,
        "Scaled to 40": 15
    }

    cell_height = 8

    # Title
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, f"Subject: {subject_name}", 0, 1, 'C')
    pdf.ln(5)

    # Headers
    pdf.set_font('Arial', 'B', 6)
    for col in columns:
        pdf.cell(col_widths.get(col, 18), cell_height, str(col), 1, 0, 'C')
    pdf.ln()

    # Data
    pdf.set_font('Arial', '', 8)
    for _, row in df.iterrows():

        if pdf.get_y() + cell_height > pdf.page_break_trigger:
            pdf.add_page()
            pdf.set_left_margin(20)

            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, f"{subject_name} (continued)", 0, 1, 'C')
            pdf.ln(5)

            pdf.set_font('Arial', 'B', 6)
            for col in columns:
                pdf.cell(col_widths.get(col, 18), cell_height, str(col), 1, 0, 'C')
            pdf.ln()

            pdf.set_font('Arial', '', 8)

        for col in columns:
            pdf.cell(col_widths.get(col, 18), cell_height, str(row[col]), 1, 0, 'C')
        pdf.ln()

    # Save to memory
    pdf_output = pdf.output(dest='S').encode('latin-1')
    return pdf_output
