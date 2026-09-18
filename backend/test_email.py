"""
ApplyMate AI – Quick Brevo Email Test
Run this LOCALLY to verify your Brevo API key and sender are working:

  cd backend
  python test_email.py your@email.com

It will send a real test email and print the Brevo API response.
"""

import asyncio
import os
import sys
import httpx

try:
    from app.core.config import settings
    BREVO_API_KEY = os.getenv("BREVO_API_KEY") or settings.BREVO_API_KEY
    EMAIL_FROM    = os.getenv("EMAIL_FROM") or settings.EMAIL_FROM
    EMAIL_FROM_NAME = getattr(settings, "EMAIL_FROM_NAME", "ApplyMate AI")
except Exception:
    BREVO_API_KEY = os.getenv("BREVO_API_KEY", "")
    EMAIL_FROM    = os.getenv("EMAIL_FROM", "noreply@applymate.ai")
    EMAIL_FROM_NAME = "ApplyMate AI"

BREVO_API     = "https://api.brevo.com/v3/smtp/email"


async def send_test(to_email: str):
    payload = {
        "sender": {"name": EMAIL_FROM_NAME, "email": EMAIL_FROM},
        "to": [{"email": to_email, "name": "Test User"}],
        "subject": "✅ ApplyMate AI – Email Test",
        "htmlContent": """
        <div style="background:#0f0f1a;padding:40px;font-family:Arial,sans-serif;text-align:center;">
          <h1 style="color:#a78bfa;">ApplyMate AI</h1>
          <p style="color:#e2e8f0;font-size:18px;">🎉 Your email setup is working!</p>
          <p style="color:#94a3b8;">This is a test email from your backend.</p>
        </div>
        """,
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "api-key": BREVO_API_KEY,
    }

    print(f"\n[SENDING] Test email to: {to_email}")
    print(f"   From: {EMAIL_FROM}")
    print(f"   API key: {BREVO_API_KEY[:20]}...")

    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.post(BREVO_API, json=payload, headers=headers)

    status_word = "SUCCESS" if resp.status_code in (200, 201) else "FAILED"
    print(f"\n[{status_word}] Status: {resp.status_code}")
    print(f"   Response: {resp.text[:500]}")

    if resp.status_code == 401:
        print("\n[!] API key is invalid. Get a new one at:")
        print("   https://app.brevo.com/settings/keys/api")
    elif resp.status_code == 403:
        print("\n[!] Sender not authorized. Verify the sender in Brevo:")
        print("   https://app.brevo.com/senders/list")
        print(f"   Add and verify: {EMAIL_FROM}")
    elif resp.status_code in (200, 201):
        print(f"\n[OK] Email sent! Check your inbox at {to_email}")


if __name__ == "__main__":
    to = sys.argv[1] if len(sys.argv) > 1 else EMAIL_FROM
    asyncio.run(send_test(to))
