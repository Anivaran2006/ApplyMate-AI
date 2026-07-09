from app.notifier.email_notifier import send_email

try:
    send_email(
        "ApplyMate AI - Test Email",
        """
        <h2>🎉 Congratulations!</h2>
        <p>Your Gmail SMTP is working successfully.</p>
        <p>This is a test email from <b>ApplyMate AI</b>.</p>
        """,
        "aniv8007@gmail.com"   # Replace with any email you want to test
    )

    print("✅ Email sent successfully!")

except Exception as e:
    print("❌ Error sending email:")
    print(e)