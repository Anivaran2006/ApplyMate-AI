import os
import resend
from dotenv import load_dotenv

load_dotenv()

resend.api_key = os.getenv("RESEND_API_KEY")

TO_EMAIL = os.getenv("TEST_EMAIL")


def send_email(subject, html_content):

    params = {
        "from": "onboarding@resend.dev",
        "to": [TO_EMAIL],
        "subject": subject,
        "html": html_content,
    }

    response = resend.Emails.send(params)

    return response