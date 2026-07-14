from app.ai.gemini_service import client


def ask_ai(question: str, notices):

    context = ""

    for notice in notices:

        context += f"""
Title: {notice.title}
Category: {notice.category}
Summary: {notice.summary or ""}
Important Dates: {notice.important_dates or ""}
Eligibility: {notice.eligibility or ""}
Action Required: {notice.action_required or ""}
Priority: {notice.priority or ""}
Type: {notice.notice_type or ""}
Link: {notice.notice_url}
"""

    prompt = f"""
You are ApplyMate AI.

You are an intelligent educational assistant.

You help students with:

- JEE
- NEET
- GATE
- UPSC
- SSC
- Banking
- Railway
- CUET
- CAT
- CLAT
- Scholarships
- Government Jobs

Latest Notices

{context}

Question:

{question}

Rules:

1. Use stored notices whenever possible.

2. If the answer is not found,
use your own knowledge.

3. Mention whether the answer
came from stored notices or
general knowledge.

4. Keep the answer concise.

5. Format nicely using bullet points.
"""

    try:

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        if hasattr(response, "text") and response.text:

            return response.text

    except Exception as e:

        print("Assistant Error:", e)

    # -----------------------------
    # Intelligent Offline Search
    # -----------------------------

    categories = [

        "JEE",
        "NEET",
        "GATE",
        "UPSC",
        "SSC",
        "BANKING",
        "RAILWAY",
        "CUET",
        "CAT",
        "CLAT"

    ]

    selected_category = None

    question_lower = question.lower()

    for cat in categories:

        if cat.lower() in question_lower:

            selected_category = cat

            break

    query_words = [

        w.lower()

        for w in question.split()

        if len(w) > 2

    ]

    matches = []

    for notice in notices:

        if (

            selected_category

            and

            notice.category.upper() != selected_category

        ):

            continue

        searchable = f"""

        {notice.title}

        {notice.category}

        {notice.summary or ""}

        {notice.eligibility or ""}

        {notice.important_dates or ""}

        {notice.action_required or ""}

        {notice.keywords or ""}

        """.lower()

        score = 0

        for word in query_words:

            if word in searchable:

                score += 1

        if score > 0:

            matches.append((score, notice))

    matches.sort(

        key=lambda x: x[0],

        reverse=True

    )

    if matches:

        answer = ""

        answer += "⚠ Gemini AI is temporarily unavailable.\n\n"

        answer += "These results were found in your ApplyMate database.\n\n"

        for _, notice in matches[:5]:

            answer += f"📌 {notice.title}\n"

            answer += f"📂 Category: {notice.category}\n"

            if notice.summary:

                answer += f"📝 Summary: {notice.summary}\n"

            if notice.important_dates:

                answer += f"📅 Dates: {notice.important_dates}\n"

            if notice.eligibility:

                answer += f"🎓 Eligibility: {notice.eligibility}\n"

            if notice.notice_url:

                answer += f"🔗 {notice.notice_url}\n"

            answer += "\n"

        return answer

    return (
        "⚠ Gemini AI is unavailable because your API quota has been exceeded.\n\n"
        "No matching notices were found in the ApplyMate database."
    )