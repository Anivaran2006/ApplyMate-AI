import asyncio

from app.notifier.telegram_notifier import send_telegram_message

CHAT_ID = "8986260447"


async def main():

    await send_telegram_message(
        CHAT_ID,
        """
🚀 *ApplyMate AI*

✅ Telegram Notifications are working!

This message was sent directly from your FastAPI project.

Congratulations 🎉
        """
    )


asyncio.run(main())