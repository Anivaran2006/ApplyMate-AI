"""
ApplyMate AI – Google Gemini Integration
Generates structured AI summaries, explanations, translations for notices.
"""

import json
import re
from typing import Optional

try:
    from tenacity import retry, stop_after_attempt, wait_exponential  # type: ignore
except ImportError:
    def retry(*args, **kwargs):  # type: ignore
        def decorator(f):
            return f
        return decorator
    def stop_after_attempt(*args, **kwargs): pass  # type: ignore
    def wait_exponential(*args, **kwargs): pass  # type: ignore

from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Initialize client using modern google-genai or legacy google.generativeai
_client = None
_model = None
_use_new_genai = False

try:
    from google import genai  # type: ignore
    if settings.GEMINI_API_KEY:
        _client = genai.Client(api_key=settings.GEMINI_API_KEY)
    _use_new_genai = True
except Exception:
    try:
        import google.generativeai as genai_legacy  # type: ignore
        if settings.GEMINI_API_KEY:
            genai_legacy.configure(api_key=settings.GEMINI_API_KEY)
            _model = genai_legacy.GenerativeModel(settings.GEMINI_MODEL)
    except Exception as e:
        logger.warning(f"Could not initialize Gemini client: {e}")


async def _generate_text_async(prompt: str) -> str:
    """Generate text using either modern google-genai or legacy SDK."""
    if _use_new_genai and _client:
        response = await _client.aio.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=prompt,
        )
        return (response.text or "").strip()
    elif _model:
        response = await _model.generate_content_async(prompt)
        return (response.text or "").strip()
    return ""


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
        text = await _generate_text_async(prompt)
        raw = _clean_json(text)
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

    return await _generate_text_async(prompt)


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

    return await _generate_text_async(prompt)


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

    return await _generate_text_async(prompt)


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


async def ask_assistant(question: str, notices: list, history: list = None) -> str:
    """Ask ApplyMate AI a question using notices context and history, with offline fallback."""
    if history is None:
        history = []

    context = ""
    for n in notices[:20]:
        context += f"""
Title: {n.title}
Category: {n.category}
Summary: {getattr(n, 'ai_summary', '') or ''}
Important Dates: {getattr(n, 'ai_important_dates', '') or ''}
Eligibility: {getattr(n, 'ai_eligibility', '') or ''}
Action Required: {getattr(n, 'ai_action_required', '') or ''}
URL: {n.url}
"""

    prompt = f"""You are ApplyMate AI, an intelligent academic advisor and educational assistant for Indian students.
You help students with JEE, NEET, CUET, GATE, CAT, UPSC, SSC, Banking, Railway, Scholarships, and government job exams.

Stored Official Notices:
{context}

Recent Chat History:
{history[-6:] if history else "None"}

Student Question:
{question}

Instructions:
1. Answer clearly, concisely, and accurately.
2. Use stored notices whenever relevant. Mention official notice titles and URLs if applicable.
3. If not found in stored notices, use your general knowledge of Indian competitive exams.
4. Format nicely using markdown bullet points and bold text.
5. Keep your response helpful, encouraging, and focused.
"""

    if settings.GEMINI_API_KEY:
        try:
            res = await _generate_text_async(prompt)
            if res:
                return res
        except Exception as e:
            logger.warning(f"Assistant Gemini error: {e}")

    # Fallback to smart keyword search in notices
    q_lower = question.lower()
    query_words = [w for w in re.findall(r"\w+", q_lower) if len(w) > 2]
    matches = []

    for n in notices:
        searchable = f"{n.title} {n.category} {getattr(n, 'ai_summary', '') or ''} {getattr(n, 'ai_eligibility', '') or ''}".lower()
        score = sum(1 for w in query_words if w in searchable)
        if score > 0:
            matches.append((score, n))

    matches.sort(key=lambda x: x[0], reverse=True)

    if matches:
        reply = "🤖 **ApplyMate AI (Database Search)**\n\nHere are the relevant notices found for your query:\n\n"
        for _, n in matches[:3]:
            reply += f"### 📌 {n.title}\n"
            reply += f"**Category:** {n.category}\n\n"
            if getattr(n, "ai_summary", None):
                reply += f"**Summary:** {n.ai_summary}\n\n"
            if getattr(n, "ai_important_dates", None):
                reply += f"**Important Dates:** {n.ai_important_dates}\n\n"
            if getattr(n, "url", None):
                reply += f"**Official Link:** [View Notice]({n.url})\n\n"
            reply += "---\n\n"
        return reply

    return (
        "Hello! I am your ApplyMate AI assistant. I can answer questions about exam dates, eligibility, "
        "and latest official notices. Could you please specify which exam (e.g. NEET, JEE, CUET, UPSC) you need help with?"
    )
