from fpdf import FPDF
import os

def create_sample_pdf(file_path):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="TAX CLAIM REIMBURSEMENT FORM", ln=True, align='C')
    pdf.ln(10)

    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, txt="Employee Name: Abhilash U Prakash", ln=True)
    pdf.cell(0, 10, txt="Financial Year: 2025-26", ln=True)
    pdf.ln(5)

    # Table Data
    pdf.set_font("Arial", '', 11)
    rows = [
        ("15/02/2026", "Apollo Pharmacy - Medicine for Parents", "80D", "12,500.00")
    ]

    for date, desc, sec, amt in rows:
        pdf.cell(30, 10, date, 1)
        pdf.cell(80, 10, desc, 1)
        pdf.cell(40, 10, sec, 1)
        pdf.cell(40, 10, amt, 1)

    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt="Total Claimed Amount: INR 12,500.00", ln=True)
    
    pdf.set_font("Arial", 'I', 10)
    pdf.ln(5)
    pdf.multi_cell(0, 5, txt="Declaration: I hereby declare that the above expenses were incurred for the purposes mentioned and are eligible for tax deduction under the prevailing laws.")

    pdf.output(file_path)
    print(f"Successfully created: {file_path}")

if __name__ == "__main__":
    target_path = r"d:\Abhilash U Prakash\Study Materials\ClaimsAdvisor\claimsadvisor\sample_claims_report.pdf"
    create_sample_pdf(target_path)
