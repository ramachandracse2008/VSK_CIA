import streamlit as st
import pdfplumber
import pandas as pd
import io
import random

st.title("📊 Internal Marks PDF to Excel Converter")

# File uploader
uploaded_file = st.file_uploader("Upload your Internal Marks PDF", type=["pdf"])

# Default subject
subject_name = "Internal Assessment"

# Valid prefixes
valid_regd_prefixes = ["26BS", "25BS", "24BS", "23BS", "22BS"]

if uploaded_file is not None:

    all_student_data = []

    with pdfplumber.open(uploaded_file) as pdf:

        # Extract subject name
        first_page_text = pdf.pages[0].extract_text()
        if first_page_text:
            for line in first_page_text.split('\n'):
                if "Subject : " in line:
                    subject_name = line.replace("Subject : ", "").strip()

        # Process pages
        for page in pdf.pages:
            table = page.extract_table()
            if table:
                for row in table[1:]:
                    clean_row = [
                        str(item).replace('\n', ' ').strip() if item else ""
                        for item in row[:4]
                    ]

                    if len(clean_row) > 1 and any(clean_row[1].startswith(prefix) for prefix in valid_regd_prefixes):

                        s_no = clean_row[0]
                        regd_no = clean_row[1]
                        student_name = clean_row[2]
                        total_marks_from_pdf_str = clean_row[3]

                        total_1_plus_2_calc = ''
                        scaled_to_40 = ''
                        total_1 = ''
                        total_2 = ''

                        assignment_1 = ''
                        seminar_quiz_1 = ''
                        ncc_nss_1 = ''
                        mid_1 = ''

                        assignment_2 = ''
                        seminar_quiz_2 = ''
                        ncc_nss_2 = ''
                        mid_2 = ''

                        try:
                            total_marks_numeric = float(total_marks_from_pdf_str)

                            total_1_plus_2_calc = round(total_marks_numeric / 0.40)
                            scaled_to_40 = round(total_1_plus_2_calc * 0.40)

                            half_total = total_1_plus_2_calc / 2
                            random_offset = random.randint(-5, 5)

                            total_1 = min(round(half_total + random_offset), 50)
                            total_2 = round(total_1_plus_2_calc - total_1)

                            # Total 1 breakdown
                            ncc_nss_1 = 10
                            assignment_1 = round(total_1 * 0.20)
                            mid_1 = round(total_1 * 0.40)
                            seminar_quiz_1 = total_1 - assignment_1 - mid_1 - ncc_nss_1

                            if seminar_quiz_1 < 0:
                                mid_1 -= abs(seminar_quiz_1)
                                seminar_quiz_1 = 0

                            # Total 2 breakdown
                            ncc_nss_2 = 10
                            assignment_2 = round(total_2 * 0.20)
                            mid_2 = round(total_2 * 0.40)
                            seminar_quiz_2 = total_2 - assignment_2 - mid_2 - ncc_nss_2

                            if seminar_quiz_2 < 0:
                                mid_2 -= abs(seminar_quiz_2)
                                seminar_quiz_2 = 0

                        except:
                            pass

                        new_student_entry = [
                            s_no, regd_no, student_name,
                            assignment_1, seminar_quiz_1, ncc_nss_1, mid_1, total_1,
                            assignment_2, seminar_quiz_2, ncc_nss_2, mid_2, total_2,
                            total_1_plus_2_calc, scaled_to_40
                        ]

                        all_student_data.append(new_student_entry)

    # Create DataFrame
    columns = [
        "S.No.", "Regd.No.", "Student Name",
        "Assignment 1", "Seminar/Quiz 1", "NCC/NSS 1", "Mid I", "Total 1",
        "Assignment 2", "Seminar/Quiz 2", "NCC/NSS 2", "Mid II", "Total 2",
        "Total 1 + Total 2", "Scaled to 40"
    ]

    df = pd.DataFrame(all_student_data, columns=columns)

    st.success(f"✅ Extracted data for subject: {subject_name}")
    st.dataframe(df)

    # Save to Excel in memory
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        pd.Series([f"Subject: {subject_name}"]).to_excel(
            writer, index=False, header=False, startrow=0
        )
        df.to_excel(writer, index=False, startrow=2)

    output.seek(0)

    # Download button
    st.download_button(
        label="📥 Download Excel File",
        data=output,
        file_name=f"{subject_name}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )