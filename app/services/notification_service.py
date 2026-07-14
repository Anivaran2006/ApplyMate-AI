import asyncio

from sqlalchemy.orm import Session

from app.database.models import Subscription
from app.notifier.telegram_notifier import send_telegram_message
from app.notifier.email_notifier import send_email


def notify_users(db: Session, notice):
    """
    Notify all users subscribed to the notice category.
    """

    subscriptions = (
        db.query(Subscription)
        .filter(Subscription.category == notice.category)
        .all()
    )

    if not subscriptions:
        print("No subscribed users found.")
        return

    telegram_sent = 0
    email_sent = 0

    for subscription in subscriptions:

        user = subscription.user

        message = f"""
🚀 *ApplyMate AI*

📰 *{notice.title}*

━━━━━━━━━━━━━━━━━━━━

📌 *Summary*
{notice.summary}

📅 *Important Dates*
{notice.important_dates}

✅ *Eligibility*
{notice.eligibility}

📝 *Action Required*
{notice.action_required}

🔗 *Official Link*
{notice.notice_url}

━━━━━━━━━━━━━━━━━━━━

Good luck! 🍀
"""

        # ---------------- TELEGRAM ----------------

        if user.telegram_chat_id and user.telegram_notifications:

            try:

                try:

                    loop = asyncio.get_running_loop()

                    loop.create_task(
                        send_telegram_message(
                            user.telegram_chat_id,
                            message
                        )
                    )

                except RuntimeError:

                    asyncio.run(
                        send_telegram_message(
                            user.telegram_chat_id,
                            message
                        )
                    )

                telegram_sent += 1

            except Exception as e:

                print(f"Telegram Error ({user.email}):", e)

        # ---------------- EMAIL ----------------

        if user.email_notifications:

            try:

                send_email(
                    subject=f"📢 {notice.title}",
                    html_content=f"""
<html>
<body>

<h2>🚀 ApplyMate AI</h2>

<h3>{notice.title}</h3>

<p><b>Summary</b></p>
<p>{notice.summary}</p>

<p><b>Important Dates</b></p>
<p>{notice.important_dates}</p>

<p><b>Eligibility</b></p>
<p>{notice.eligibility}</p>

<p><b>Action Required</b></p>
<p>{notice.action_required}</p>

<p>
<b>Official Link</b><br>
<a href="{notice.notice_url}">
{notice.notice_url}
</a>
</p>

<hr>

<p>Good luck! 🍀</p>

</body>
</html>
""",
                    to_email=user.email
                )

                email_sent += 1

            except Exception as e:

                print(f"Email Error ({user.email}):", e)

    print("=" * 50)
    print(f"Subscriptions Found : {len(subscriptions)}")
    print(f"Telegram Sent       : {telegram_sent}")
    print(f"Email Sent          : {email_sent}")
    print("=" * 50)