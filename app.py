import streamlit as st
import pdfplumber
import pandas as pd
import io
import random
from fpdf import FPDF

st.title("📊 Internal Marks PDF → Excel & PDF Converter")

uploaded_file = st.file_uploader("Upload Internal Marks PDF", type=["pdf"])

valid_regd_prefixes = ["26BS", "25BS", "24BS", "23BS", "22BS"]

def generate_pdf(df, subject_name):
    pdf = FPDF('L', 'mm', 'A4')
    pdf.add_page()
    pdf.set_left_margin(20)

    columns = df.columns.tolist()

    col_widths = {
        "S.No.": 10, "Regd.No.": 20, "Student Name": 55,
        "Assignment 1": 15, "Seminar/Quiz 1": 18, "NCC/NSS 1": 15,
        "Mid I": 12, "Total 1": 12,
        "Assignment 2": 15, "Seminar/Quiz 2": 18, "NCC/NSS 2": 15,
        "Mid II": 12, "Total 2": 12,
        "Total 1 + Total 2": 20, "Scaled to 40": 15
    }

    cell_height = 8

    # Title
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, f"Subject: {subject_name}", 0, 1, 'C')
    pdf.ln(5)

    # Header
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

    return pdf.output(dest='S').encode('latin-1')


if uploaded_file is not None:

    all_student_data = []
    subject_name = "Internal Assessment"

    with pdfplumber.open(uploaded_file) as pdf:

        first_page_text = pdf.pages[0].extract_text()
        if first_page_text:
            for line in first_page_text.split('\n'):
                if "Subject : " in line:
                    subject_name = line.replace("Subject : ", "").strip()

        for page in pdf.pages:
            table = page.extract_table()
            if table:
                for row in table[1:]:

                    clean_row = [
                        str(item).replace('\n', ' ').strip() if item else ""
                        for item in row[:4]
                    ]

                    if len(clean_row) > 1 and any(clean_row[1].startswith(prefix) for prefix in valid_regd_prefixes):

                        s_no, regd_no, student_name, total_str = clean_row

                        try:
                            total = float(total_str)

                            total_1_plus_2 = round(total / 0.40)
                            scaled_40 = round(total_1_plus_2 * 0.40)

                            half = total_1_plus_2 / 2
                            total_1 = min(round(half + random.randint(-5, 5)), 50)
                            total_2 = round(total_1_plus_2 - total_1)

                            # Breakdown
                            def split_marks(t):
                                ncc = 10
                                assign = round(t * 0.20)
                                mid = round(t * 0.40)
                                seminar = t - assign - mid - ncc
                                if seminar < 0:
                                    mid -= abs(seminar)
                                    seminar = 0
                                return assign, seminar, ncc, mid

                            a1, s1, n1, m1 = split_marks(total_1)
                            a2, s2, n2, m2 = split_marks(total_2)

                        except:
                            a1 = s1 = n1 = m1 = total_1 = ''
                            a2 = s2 = n2 = m2 = total_2 = ''
                            total_1_plus_2 = scaled_40 = ''

                        all_student_data.append([
                            s_no, regd_no, student_name,
                            a1, s1, n1, m1, total_1,
                            a2, s2, n2, m2, total_2,
                            total_1_plus_2, scaled_40
                        ])

    columns = [
        "S.No.", "Regd.No.", "Student Name",
        "Assignment 1", "Seminar/Quiz 1", "NCC/NSS 1", "Mid I", "Total 1",
        "Assignment 2", "Seminar/Quiz 2", "NCC/NSS 2", "Mid II", "Total 2",
        "Total 1 + Total 2", "Scaled to 40"
    ]

    df = pd.DataFrame(all_student_data, columns=columns)

    st.success(f"✅ Subject: {subject_name}")
    st.dataframe(df)

    # Excel
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
        pd.Series([f"Subject: {subject_name}"]).to_excel(writer, index=False, header=False)
        df.to_excel(writer, index=False, startrow=2)

    excel_buffer.seek(0)

    st.download_button(
        "📥 Download Excel",
        data=excel_buffer,
        file_name=f"{subject_name}.xlsx"
    )

    # PDF
    pdf_data = generate_pdf(df, subject_name)

    st.download_button(
        "📄 Download PDF",
        data=pdf_data,
        file_name=f"{subject_name}.pdf",
        mime="application/pdf"
    )
