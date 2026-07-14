import os
import smtplib

from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")


def send_email(
    subject: str,
    html_content: str,
    to_email: str
):
    """
    Send an HTML email using Gmail SMTP.
    """

    if not EMAIL_ADDRESS or not EMAIL_APP_PASSWORD:
        raise ValueError(
            "EMAIL_ADDRESS or EMAIL_APP_PASSWORD is missing in .env"
        )

    msg = EmailMessage()

    msg["Subject"] = subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email

    msg.set_content(
        "Please view this email in an HTML-supported client."
    )

    msg.add_alternative(
        html_content,
        subtype="html"
    )

    try:

        with smtplib.SMTP_SSL(
            "smtp.gmail.com",
            465
        ) as smtp:

            smtp.login(
                EMAIL_ADDRESS,
                EMAIL_APP_PASSWORD
            )

            smtp.send_message(msg)

        print(f"✅ Email sent to {to_email}")

        return True

    except Exception as e:

        print(f"❌ Failed to send email to {to_email}")
        print(e)

        return False