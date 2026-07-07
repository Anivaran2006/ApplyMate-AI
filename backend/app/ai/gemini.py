"""
ApplyMate AI – Google Gemini Integration
Generates structured AI summaries, explanations, translations for notices.
"""

import json
import re
from typing import Optional

import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Configure Gemini client once
genai.configure(api_key=settings.GEMINI_API_KEY)
_model = genai.GenerativeModel(settings.GEMINI_MODEL)


def _clean_json(text: str) -> str:
    """Strip markdown code fences from Gemini's JSON output."""
    text = re.sub(r"```json\s*", "", text)
    text = re.sub(r"```\s*", "", text)
    return text.strip()


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def generate_notice_summary(title: str, raw_content: str) -> dict:
    """
    Generate a structured AI summary for an educational notice.
    Returns a dict with: summary, explanation, important_dates, action_required,
    eligibility, deadline.
    """
    if not settings.GEMINI_API_KEY:
        logger.warning("GEMINI_API_KEY not set – returning placeholder AI fields")
        return _placeholder_summary(title)

    prompt = f"""You are an expert educational counselor helping Indian students understand official exam and scholarship notices.

Analyze the following educational notice and return a JSON object with exactly these keys:

{{
  "summary": "2-3 sentence plain-language summary (max 150 words)",
  "explanation": "Simple explanation for a student with no prior knowledge (max 200 words)",
  "important_dates": "List all dates and deadlines mentioned, formatted as bullet points",
  "action_required": "What the student must do and by when (max 100 words)",
  "eligibility": "Who is eligible to apply or participate (max 100 words)",
  "deadline": "The single most important deadline in DD-MMM-YYYY format, or 'Not specified'"
}}

Notice Title: {title}

Notice Content:
{raw_content[:3000]}

Return ONLY valid JSON, no markdown fences, no explanation text."""

    try:
        response = await _model.generate_content_async(prompt)
        raw = _clean_json(response.text)
        data = json.loads(raw)
        return {
            "summary": data.get("summary", ""),
            "explanation": data.get("explanation", ""),
            "important_dates": data.get("important_dates", ""),
            "action_required": data.get("action_required", ""),
            "eligibility": data.get("eligibility", ""),
            "deadline": data.get("deadline", "Not specified"),
        }
    except json.JSONDecodeError:
        logger.error(f"Gemini returned invalid JSON for notice: {title[:60]}")
        return _placeholder_summary(title)
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        raise


@retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=2, max=8))
async def explain_more(title: str, summary: str) -> str:
    """Return a detailed plain-English explanation of the notice."""
    if not settings.GEMINI_API_KEY:
        return "Gemini API key not configured."

    prompt = f"""You are explaining an Indian educational notice to a confused student.

Notice: {title}
Summary: {summary}

Give a detailed, friendly explanation in 300-400 words. Use simple language, no jargon.
Break it into: What is this? Why does it matter? What should you do?"""

    response = await _model.generate_content_async(prompt)
    return response.text.strip()


@retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=2, max=8))
async def translate_to_hindi(text: str) -> str:
    """Translate notice summary to Hindi."""
    if not settings.GEMINI_API_KEY:
        return "Gemini API key not configured."

    prompt = f"""Translate the following educational notice summary to Hindi.
Use simple, clear Hindi that students can understand.
Keep any dates, exam names, and proper nouns as-is.

Text to translate:
{text}

Provide ONLY the Hindi translation, no English text."""

    response = await _model.generate_content_async(prompt)
    return response.text.strip()


@retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=2, max=8))
async def re_summarize(title: str, raw_content: str) -> str:
    """Generate a fresh, concise summary of the notice."""
    if not settings.GEMINI_API_KEY:
        return "Gemini API key not configured."

    prompt = f"""Create a fresh, concise summary of this educational notice in exactly 3 bullet points.
Each bullet should be one clear, actionable sentence.

Notice: {title}
Content: {raw_content[:2000]}

Format:
• [Key point 1]
• [Key point 2]
• [Key point 3]"""

    response = await _model.generate_content_async(prompt)
    return response.text.strip()


def _placeholder_summary(title: str) -> dict:
    """Return placeholder when Gemini is unavailable."""
    return {
        "summary": f"Official notice: {title}. Please visit the official website for full details.",
        "explanation": "AI processing is currently unavailable. Please read the original notice.",
        "important_dates": "See the original notice for dates.",
        "action_required": "Visit the official website to take action.",
        "eligibility": "See the original notice for eligibility criteria.",
        "deadline": "Not specified",
    }


async def detect_category(title: str) -> str:
    """Detect notice category based on keyword matching."""
    title_upper = title.upper()
    keyword_map = {
        "NEET": ["NEET", "NATIONAL ELIGIBILITY"],
        "JEE": ["JEE", "JOINT ENTRANCE"],
        "CUET": ["CUET", "COMMON UNIVERSITY"],
        "GATE": ["GATE", "GRADUATE APTITUDE"],
        "CAT": ["CAT", "COMMON ADMISSION TEST"],
        "UPSC": ["UPSC", "CIVIL SERVICES", "IAS", "IPS"],
        "SSC": ["SSC", "STAFF SELECTION"],
        "BANKING": ["IBPS", "SBI", "RBI", "BANKING", "BANK PO", "CLERK"],
        "SCHOLARSHIPS": ["SCHOLARSHIP", "FELLOWSHIP", "STIPEND", "MERIT"],
    }
    for category, keywords in keyword_map.items():
        if any(kw in title_upper for kw in keywords):
            return category
    return "GENERAL"
