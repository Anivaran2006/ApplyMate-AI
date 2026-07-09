from app.ai.gemini_service import summarize_notice

result = summarize_notice(
    "JEE Main Registration Started",
    "Registration for JEE Main 2026 has started. Last date is 25 July. Candidates who passed Class 12 can apply."
)

print(result)