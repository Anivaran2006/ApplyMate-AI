from app.notifier.resend_notifier import send_email

response = send_email(
    "ApplyMate AI Test",
    "<h1>ApplyMate AI</h1><p>Resend is working.</p>"
)

print(response)