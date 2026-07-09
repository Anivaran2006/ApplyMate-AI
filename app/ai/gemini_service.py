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
You are an educational notice assistant.

Analyze the notice below and return ONLY valid JSON.

Title:
{title}

Description:
{description}

Return exactly in this format:

{{
  "summary": "...",
  "important_dates": "...",
  "eligibility": "...",
  "action_required": "...",
  "keywords": ["...", "..."]
}}
"""

    try:

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )

        text = response.text.strip()

        # Remove Markdown formatting if present
        if text.startswith("```"):
            text = (
                text.replace("```json", "")
                .replace("```", "")
                .strip()
            )

        result = json.loads(text)

    except Exception as e:

        print("Gemini Error:", e)

        result = {
            "summary": description[:300],
            "important_dates": "",
            "eligibility": "",
            "action_required": "",
            "keywords": []
        }

    # ---------- Normalize Fields ----------

    result["summary"] = str(result.get("summary", ""))

    result["important_dates"] = str(
        result.get("important_dates", "")
    )

    result["eligibility"] = str(
        result.get("eligibility", "")
    )

    result["action_required"] = str(
        result.get("action_required", "")
    )

    keywords = result.get("keywords", "")

    if isinstance(keywords, list):
        keywords = ", ".join(keywords)

    result["keywords"] = str(keywords)

    return result