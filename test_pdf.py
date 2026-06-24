from app.services.pdf_service import extract_pdf_text

pdf_url = "https://nta.ac.in/Download/Notice/Notice_20260621193322.pdf"

text = extract_pdf_text(pdf_url)

print(text[:3000])