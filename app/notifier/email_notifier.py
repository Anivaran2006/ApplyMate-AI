import smtplib
import os

from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")


def send_email(subject, html_content, to_email):

    print("=" * 50)
    print("EMAIL_ADDRESS:", EMAIL_ADDRESS)
    print("APP PASSWORD EXISTS:", EMAIL_APP_PASSWORD is not None)
    print("Sending email to:", to_email)
    print("=" * 50)

    msg = EmailMessage()

    msg["Subject"] = subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email

    msg.add_alternative(
        html_content,
        subtype="html"
    )

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:

            smtp.login(
                EMAIL_ADDRESS,
                EMAIL_APP_PASSWORD
            )

            smtp.send_message(msg)

        print("✅ Email sent successfully!")

    except Exception as e:
        print("❌ Email sending failed!")
        print(type(e).__name__)
        print(str(e))
        raise