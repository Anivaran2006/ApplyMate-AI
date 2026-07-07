"""
ApplyMate AI – Telegram Notification Sender
"""

from typing import Optional

import httpx

from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

TELEGRAM_API = "https://api.telegram.org/bot{token}/{method}"


def _api_url(method: str) -> str:
    return TELEGRAM_API.format(token=settings.TELEGRAM_BOT_TOKEN, method=method)


async def send_message(chat_id: str, text: str, parse_mode: str = "HTML") -> bool:
    """
    Send a Telegram message to a chat_id.
    Returns True on success, False on failure.
    """
    if not settings.TELEGRAM_BOT_TOKEN:
        logger.warning("TELEGRAM_BOT_TOKEN not set – skipping Telegram notification")
        return False

    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": False,
    }

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(_api_url("sendMessage"), json=payload)
            data = resp.json()
            if data.get("ok"):
                return True
            else:
                logger.error(f"Telegram API error: {data.get('description')}")
                return False
    except Exception as e:
        logger.error(f"Telegram send failed for chat_id={chat_id}: {e}")
        return False


def build_notice_message(notice: dict) -> str:
    """Build a richly formatted HTML Telegram message for a notice."""
    category_emoji = {
        "NEET": "🩺", "JEE": "⚡", "CUET": "🎓", "GATE": "🔬",
        "CAT": "📊", "UPSC": "🏛️", "SSC": "📋", "BANKING": "🏦",
        "SCHOLARSHIPS": "🌟", "GENERAL": "📢",
    }
    emoji = category_emoji.get(notice.get("category", "GENERAL"), "📢")

    title = notice.get("title", "New Notice")[:200]
    category = notice.get("category", "GENERAL")
    summary = notice.get("ai_summary", "")[:400] if notice.get("ai_summary") else ""
    deadline = notice.get("ai_deadline", "")
    url = notice.get("url", "")

    lines = [
        f"{emoji} <b>New {category} Notice</b>",
        f"",
        f"📌 <b>{title}</b>",
    ]

    if summary:
        lines += ["", f"📝 <b>Summary:</b>", summary]

    if deadline and deadline != "Not specified":
        lines += ["", f"⏰ <b>Deadline:</b> {deadline}"]

    if url:
        lines += ["", f"🔗 <a href='{url}'>Read Full Notice</a>"]

    lines += ["", "─────────────────", "🤖 <i>Powered by ApplyMate AI</i>"]

    return "\n".join(lines)


async def notify_user(chat_id: str, notice: dict) -> bool:
    """Send a formatted notice notification to a user's Telegram."""
    message = build_notice_message(notice)
    return await send_message(chat_id, message)


async def send_welcome_message(chat_id: str, user_name: str) -> bool:
    """Send a welcome message when a user connects their Telegram."""
    text = (
        f"👋 <b>Welcome to ApplyMate AI, {user_name}!</b>\n\n"
        f"Your Telegram is now connected. You'll receive instant notifications "
        f"for all your subscribed exam categories.\n\n"
        f"🎯 Make sure to set your category preferences on the dashboard.\n\n"
        f"🤖 <i>Powered by ApplyMate AI</i>"
    )
    return await send_message(chat_id, text)
