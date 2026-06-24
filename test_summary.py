from app.services.pdf_service import extract_pdf_text
from app.services.summary_service import create_summary

pdf_url = "https://nta.ac.in/Download/Notice/Notice_20260621193322.pdf"

text = extract_pdf_text(pdf_url)

summary = create_summary(text)

print(summary)