import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

model = genai.GenerativeModel("gemini-2.0-flash")


def create_summary(text):

    prompt = f"""
    Summarize this exam notification for students.

    Include:
    1. Main purpose
    2. Important dates
    3. Eligibility
    4. Fees
    5. Required documents

    Notification:

    {text[:10000]}
    """

    try:

        response = model.generate_content(prompt)

        return response.text

    except Exception as e:

        print("Gemini Error:", e)

        return (
    text[:1000]
    + "\n\n[AI Summary unavailable - showing extracted notice text]"
)