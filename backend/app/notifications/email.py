"""
ApplyMate AI – Email Notification Sender (Brevo / Sendinblue)
"""

from typing import Optional

import httpx

from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

BREVO_API = "https://api.brevo.com/v3/smtp/email"


def _build_html_email(notice: dict) -> str:
    """Build a beautiful HTML email body for a notice."""
    title = notice.get("title", "New Notice")
    category = notice.get("category", "GENERAL")
    summary = notice.get("ai_summary", "Please visit the link for details.")
    explanation = notice.get("ai_explanation", "")
    dates = notice.get("ai_important_dates", "")
    action = notice.get("ai_action_required", "")
    deadline = notice.get("ai_deadline", "")
    url = notice.get("url", "#")

    category_colors = {
        "NEET": "#ef4444", "JEE": "#3b82f6", "CUET": "#8b5cf6",
        "GATE": "#10b981", "CAT": "#f59e0b", "UPSC": "#6366f1",
        "SSC": "#14b8a6", "BANKING": "#f97316", "SCHOLARSHIPS": "#ec4899",
        "GENERAL": "#6b7280",
    }
    color = category_colors.get(category, "#6b7280")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>New {category} Notice – ApplyMate AI</title>
</head>
<body style="margin:0;padding:0;background-color:#080B0A;font-family:'Segoe UI',Arial,sans-serif;">
  <div style="max-width:600px;margin:0 auto;padding:20px;">
    <!-- Header -->
    <div style="background:#101512;border:1px solid rgba(255,255,255,0.08);border-radius:12px 12px 0 0;padding:28px;text-align:center;">
      <h1 style="margin:0;color:#F0F3EF;font-size:24px;font-weight:800;letter-spacing:-0.5px;">
        ApplyMate <span style="color:#B6F36B;">AI</span>
      </h1>
      <p style="margin:6px 0 0;color:#A1ADA5;font-size:13px;">Autonomous Examination Intelligence</p>
    </div>

    <!-- Category Badge -->
    <div style="background:#151C18;border-left:1px solid rgba(255,255,255,0.08);border-right:1px solid rgba(255,255,255,0.08);padding:16px 28px;display:flex;align-items:center;justify-content:space-between;">
      <span style="background:rgba(182,243,107,0.12);color:#B6F36B;border:1px solid rgba(182,243,107,0.25);padding:4px 14px;border-radius:6px;font-size:12px;font-weight:700;">
        {category}
      </span>
      <span style="color:#727E76;font-size:12px;">Verified Source</span>
    </div>

    <!-- Title -->
    <div style="background:#151C18;border-left:4px solid {color};border-right:1px solid rgba(255,255,255,0.08);padding:24px 28px;">
      <h2 style="margin:0;color:#F0F3EF;font-size:18px;line-height:1.4;">{title}</h2>
    </div>

    <!-- Summary -->
    <div style="background:#101512;border-left:1px solid rgba(255,255,255,0.08);border-right:1px solid rgba(255,255,255,0.08);padding:20px 28px;">
      <h3 style="margin:0 0 10px;color:#B6F36B;font-size:13px;text-transform:uppercase;letter-spacing:1px;">
        AI Distilled Summary
      </h3>
      <p style="margin:0;color:#A1ADA5;line-height:1.6;font-size:14px;">{summary}</p>
    </div>

    {"<!-- Important Dates --><div style='background:#151C18;border-left:1px solid rgba(255,255,255,0.08);border-right:1px solid rgba(255,255,255,0.08);padding:20px 28px;border-top:1px solid rgba(255,255,255,0.06);'><h3 style='margin:0 0 8px;color:#FBBF24;font-size:13px;text-transform:uppercase;letter-spacing:1px;'>Important Dates</h3><p style='margin:0;color:#A1ADA5;line-height:1.6;font-size:14px;white-space:pre-line;'>" + dates + "</p></div>" if dates else ""}

    {"<!-- Deadline --><div style='background:#101512;border-left:1px solid rgba(255,255,255,0.08);border-right:1px solid rgba(255,255,255,0.08);padding:14px 28px;border-top:1px solid rgba(255,255,255,0.06);'><p style='margin:0;color:#B6F36B;font-weight:600;font-size:14px;'>Key Deadline: " + deadline + "</p></div>" if deadline and deadline != "Not specified" else ""}

    {"<!-- Action Required --><div style='background:#151C18;border-left:1px solid rgba(255,255,255,0.08);border-right:1px solid rgba(255,255,255,0.08);padding:20px 28px;border-top:1px solid rgba(255,255,255,0.06);'><h3 style='margin:0 0 8px;color:#38BDF8;font-size:13px;text-transform:uppercase;letter-spacing:1px;'>Action Required</h3><p style='margin:0;color:#A1ADA5;line-height:1.6;font-size:14px;'>" + action + "</p></div>" if action else ""}

    <!-- CTA Button -->
    <div style="background:#101512;border:1px solid rgba(255,255,255,0.08);border-top:none;padding:24px 28px;text-align:center;">
      <a href="{url}" style="display:inline-block;background:#B6F36B;color:#080B0A;text-decoration:none;padding:12px 32px;border-radius:6px;font-weight:700;font-size:14px;">
        View Official Circular Document →
      </a>
    </div>

    <!-- Footer -->
    <div style="background:#080B0A;padding:20px;text-align:center;">
      <p style="margin:0;color:#727E76;font-size:12px;">
        You are receiving this because you subscribed to {category} alerts on ApplyMate AI.<br>
        Direct primary source notifications.
      </p>
    </div>
  </div>
</body>
</html>"""
    return html


async def send_email(
    to_email: str,
    to_name: str,
    subject: str,
    html_content: str,
) -> bool:
    """
    Send an email via Brevo API.
    Returns True on success, False on failure.
    """
    if not settings.BREVO_API_KEY:
        logger.warning("BREVO_API_KEY not set – skipping email notification")
        return False

    payload = {
        "sender": {"name": settings.EMAIL_FROM_NAME, "email": settings.EMAIL_FROM},
        "to": [{"email": to_email, "name": to_name}],
        "subject": subject,
        "htmlContent": html_content,
    }

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "api-key": settings.BREVO_API_KEY,
    }

    try:
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(BREVO_API, json=payload, headers=headers)
            if resp.status_code in (200, 201):
                return True
            else:
                logger.error(f"Brevo API error {resp.status_code}: {resp.text[:200]}")
                return False
    except Exception as e:
        logger.error(f"Email send failed to {to_email}: {e}")
        return False


async def notify_user_email(to_email: str, to_name: str, notice: dict) -> bool:
    """Send a formatted notice email to a user."""
    category = notice.get("category", "GENERAL")
    title = notice.get("title", "New Notice")[:80]
    subject = f"🎓 New {category} Notice: {title}"
    html = _build_html_email(notice)
    return await send_email(to_email, to_name, subject, html)


async def send_welcome_email(to_email: str, to_name: str) -> bool:
    """Send a welcome email after registration."""
    subject = "Welcome to ApplyMate AI 🚀"
    html = f"""<!DOCTYPE html>
<html><body style="background:#0f0f1a;font-family:'Segoe UI',Arial,sans-serif;margin:0;padding:20px;">
<div style="max-width:600px;margin:0 auto;background:linear-gradient(135deg,#1e1e3f,#2d2d5e);border-radius:16px;padding:40px;text-align:center;">
  <h1 style="color:#a78bfa;margin:0 0 8px;">Welcome to ApplyMate AI!</h1>
  <p style="color:#c4b5fd;font-size:16px;">Hi {to_name}, you're all set.</p>
  <p style="color:#94a3b8;line-height:1.7;">
    You'll now receive AI-powered summaries of important educational notices
    for your subscribed categories. Never miss a deadline again!
  </p>
  <p style="color:#7c3aed;font-weight:700;margin-top:32px;">Team ApplyMate AI 🤖</p>
</div>
</body></html>"""
    return await send_email(to_email, to_name, subject, html)


async def send_reset_password_email(
    to_email: str,
    token: str,
    to_name: str = "",
    frontend_url: str = "",
) -> bool:
    """Send a password reset email with a secure token link."""
    base = frontend_url or settings.FRONTEND_URL
    reset_link = f"{base}/reset-password.html?token={token}"
    display_name = to_name or to_email
    subject = "Reset your ApplyMate AI password 🔐"
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Reset Password – ApplyMate AI</title>
</head>
<body style="margin:0;padding:0;background-color:#0f0f1a;font-family:'Segoe UI',Arial,sans-serif;">
  <div style="max-width:600px;margin:0 auto;padding:20px;">
    <!-- Header -->
    <div style="background:linear-gradient(135deg,#1e1e3f,#2d2d5e);border-radius:16px 16px 0 0;padding:32px;text-align:center;">
      <h1 style="margin:0;color:#a78bfa;font-size:28px;font-weight:800;letter-spacing:-0.5px;">
        ApplyMate <span style="color:#7c3aed;">AI</span>
      </h1>
      <p style="margin:8px 0 0;color:#c4b5fd;font-size:14px;">Password Reset Request</p>
    </div>

    <!-- Body -->
    <div style="background:#1e1e3f;padding:32px;">
      <p style="color:#e2e8f0;font-size:16px;line-height:1.7;margin:0 0 24px;">
        Hi {display_name}, we received a request to reset the password for your ApplyMate AI account.
        Click the button below to set a new password. This link will expire in <strong>1 hour</strong>.
      </p>

      <div style="text-align:center;margin:32px 0;">
        <a href="{reset_link}" style="display:inline-block;background:linear-gradient(135deg,#7c3aed,#5b21b6);color:white;text-decoration:none;padding:16px 40px;border-radius:100px;font-weight:700;font-size:16px;letter-spacing:0.5px;">
          🔐 Reset My Password
        </a>
      </div>

      <p style="color:#94a3b8;font-size:13px;line-height:1.7;margin:0;">
        If you didn't request a password reset, you can safely ignore this email.
        Your password will not be changed until you click the button above and create a new one.
      </p>

      <div style="margin-top:24px;padding:16px;background:rgba(124,58,237,0.1);border:1px solid rgba(124,58,237,0.3);border-radius:8px;">
        <p style="color:#a78bfa;font-size:12px;margin:0;">
          If the button doesn't work, copy and paste this link into your browser:<br>
          <a href="{reset_link}" style="color:#7c3aed;word-break:break-all;">{reset_link}</a>
        </p>
      </div>
    </div>

    <!-- Footer -->
    <div style="background:#0f0f1a;padding:20px;text-align:center;border-radius:0 0 16px 16px;">
      <p style="margin:0;color:#4b5563;font-size:12px;">
        This email was sent by ApplyMate AI.<br>
        If you have any issues, contact us at support@applymate.ai
      </p>
    </div>
  </div>
</body>
</html>"""
    return await send_email(to_email, display_name, subject, html)
