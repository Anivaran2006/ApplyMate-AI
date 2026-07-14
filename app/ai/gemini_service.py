import os
import json

from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def summarize_notice(title: str, description: str):

    prompt = f"""
You are an AI assistant for ApplyMate AI.

Analyze the following educational notice.

Title:
{title}

Description:
{description}

Return ONLY valid JSON.

{{
  "summary": "...",
  "important_dates": "...",
  "eligibility": "...",
  "action_required": "...",
  "keywords": ["...", "..."],

  "priority": "HIGH | MEDIUM | LOW",

  "notice_type":
  "Registration | Admit Card | Result | Answer Key | Counselling | Recruitment | Scholarship | General",

  "deadline": "YYYY-MM-DD or null",

  "days_left": 0,

  "translated_summary": "Hindi translation of summary"
}}

Rules:

1. Return ONLY JSON.
2. Do not use Markdown.
3. If a field is unavailable use null.
4. days_left should be an integer.
5. priority must be HIGH, MEDIUM or LOW.
"""

    try:

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        text = response.text.strip()

        print("\n========== GEMINI RAW RESPONSE ==========")
        print(text)
        print("=========================================\n")

        if text.startswith("```"):

            text = (
                text.replace("```json", "")
                .replace("```", "")
                .strip()
            )

        start = text.find("{")
        end = text.rfind("}")

        if start != -1 and end != -1:
            text = text[start:end + 1]

        result = json.loads(text)

    except Exception as e:

        print("Gemini Error:", e)

        result = {

            "summary": description[:300],

            "important_dates": "",

            "eligibility": "",

            "action_required": "",

            "keywords": [],

            "priority": "LOW",

            "notice_type": "General",

            "deadline": None,

            "days_left": None,

            "translated_summary": ""

        }

    # ---------------- Normalize ----------------

    result["summary"] = str(
        result.get("summary", "")
    )

    result["important_dates"] = str(
        result.get("important_dates", "")
    )

    result["eligibility"] = str(
        result.get("eligibility", "")
    )

    result["action_required"] = str(
        result.get("action_required", "")
    )

    keywords = result.get("keywords", [])

    if isinstance(keywords, list):
        keywords = ", ".join(keywords)

    result["keywords"] = str(keywords)

    result["priority"] = str(
        result.get("priority", "LOW")
    ).upper()

    result["notice_type"] = str(
        result.get("notice_type", "General")
    )

    result["deadline"] = result.get(
        "deadline"
    )

    try:
        result["days_left"] = int(
            result.get("days_left", 0)
        )
    except:
        result["days_left"] = None

    result["translated_summary"] = str(
        result.get(
            "translated_summary",
            ""
        )
    )

    return result