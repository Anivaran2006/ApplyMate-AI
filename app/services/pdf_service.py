import requests
from pypdf import PdfReader

def extract_pdf_text(pdf_url):

    response = requests.get(pdf_url)

    with open("temp_notice.pdf", "wb") as pdf_file:
        pdf_file.write(response.content)

    reader = PdfReader("temp_notice.pdf")

    text = ""

    for page in reader.pages:
        extracted = page.extract_text()

        if extracted:
            text += extracted

    return text