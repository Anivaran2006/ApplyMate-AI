"""
ApplyMate AI – Scraper, Scheduler & Notification Service Tests
Verifies scraper parsing, deduplication hash, scheduler lifecycle, and notification dispatches.
"""

import asyncio
from unittest.mock import AsyncMock, patch
import pytest

from app.notifications.email import _build_html_email, notify_user_email, send_email
from app.notifications.telegram import build_notice_message, notify_user, send_message, send_welcome_message
from app.scraper.nta_scraper import compute_hash, parse_nta_notices
from app.scraper.scheduler import _scheduler, start_scheduler, stop_scheduler


def test_compute_hash_deterministic():
    """Verify SHA-256 hash is deterministic and whitespace/case insensitive."""
    h1 = compute_hash("NEET UG 2026 Notification", "https://nta.ac.in/neet.pdf")
    h2 = compute_hash("  NEET UG 2026 Notification  ", "https://nta.ac.in/neet.pdf")
    h3 = compute_hash("JEE Main 2026 Notification", "https://nta.ac.in/neet.pdf")

    assert h1 == h2
    assert len(h1) == 64
    assert h1 != h3


def test_parse_nta_notices_html():
    """Verify parsing notice table items from simulated HTML."""
    html_content = """
    <html>
      <body>
        <table>
          <tr>
            <td>01-02-2026</td>
            <td><a href="/Uploads/Notice_JEE_2026.pdf">Joint Entrance Examination (Main) - 2026 Session 1 Score Card</a></td>
          </tr>
          <tr>
            <td>05-02-2026</td>
            <td><a href="https://exams.nta.ac.in/NEET/Notice_NEET_2026.pdf">NEET (UG) 2026 - National Eligibility Cum Entrance Test Application Portal Open</a></td>
          </tr>
        </table>
      </body>
    </html>
    """
    notices = parse_nta_notices(html_content)
    assert len(notices) == 2
    assert "Joint Entrance" in notices[0]["title"]
    assert notices[0]["url"] == "https://nta.ac.in/Uploads/Notice_JEE_2026.pdf"
    assert "NEET" in notices[1]["title"]
    assert notices[1]["url"] == "https://exams.nta.ac.in/NEET/Notice_NEET_2026.pdf"
    assert len(notices[0]["content_hash"]) == 64


def test_build_html_email_template():
    """Verify HTML email template generates valid markup with ApplyMate Midnight tokens."""
    sample_notice = {
        "title": "NEET UG 2026 Examination Schedule",
        "category": "NEET",
        "ai_summary": "Application closes March 15.",
        "ai_important_dates": "15 March 2026",
        "ai_action_required": "Submit application form online",
        "ai_deadline": "15 March 2026",
        "url": "https://exams.nta.ac.in/NEET",
    }
    html = _build_html_email(sample_notice)
    assert "ApplyMate" in html
    assert "#B6F36B" in html
    assert "NEET UG 2026 Examination Schedule" in html
    assert "Application closes March 15." in html
    assert "https://exams.nta.ac.in/NEET" in html


def test_telegram_build_notice_message():
    """Verify Telegram message builder creates formatted HTML."""
    sample_notice = {
        "title": "UPSC Civil Services Prelims 2026 Released",
        "category": "UPSC",
        "ai_summary": "Notification released for 1,056 vacancies.",
        "ai_deadline": "05 March 2026",
        "url": "https://upsc.gov.in",
    }
    msg = build_notice_message(sample_notice)
    assert "UPSC" in msg
    assert "UPSC Civil Services Prelims 2026 Released" in msg
    assert "Notification released for 1,056 vacancies." in msg
    assert "05 March 2026" in msg
    assert "ApplyMate AI" in msg


@pytest.mark.asyncio
@patch("app.notifications.telegram.send_message", new_callable=AsyncMock)
async def test_telegram_notification_dispatch(mock_send):
    """Verify Telegram message dispatch formatting and delivery."""
    mock_send.return_value = True

    sample_notice = {
        "title": "UPSC Civil Services Prelims 2026 Released",
        "category": "UPSC",
        "ai_summary": "Notification released for 1,056 vacancies.",
        "url": "https://upsc.gov.in",
    }

    success = await notify_user("123456789", sample_notice)
    assert success is True
    mock_send.assert_awaited_once()
    args, kwargs = mock_send.await_args
    assert args[0] == "123456789"
    assert "UPSC Civil Services" in args[1]


@pytest.mark.asyncio
async def test_scheduler_lifecycle():
    """Verify scheduler can start and stop cleanly."""
    start_scheduler()
    assert _scheduler.running is True
    # Calling start again while running is safe
    start_scheduler()
    assert _scheduler.running is True

    stop_scheduler()
    await asyncio.sleep(0.05)
    assert _scheduler.running is False
