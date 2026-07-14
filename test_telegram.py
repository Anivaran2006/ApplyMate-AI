import os
import asyncio

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes
)

from app.database.database import SessionLocal
from app.services.telegram_auth_service import connect_telegram_account

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not context.args:

        await update.message.reply_text(
            "❌ Invalid authorization link."
        )
        return

    token = context.args[0]

    chat_id = str(update.effective_chat.id)

    db = SessionLocal()

    try:

        user = connect_telegram_account(
            db,
            token,
            chat_id
        )

        if not user:

            await update.message.reply_text(
                "❌ Invalid or expired link."
            )

            return

        await update.message.reply_text(
            f"""
✅ Telegram connected successfully!

Welcome {user.email}

You will now receive ApplyMate AI notifications.
"""
        )

    finally:

        db.close()


def main():

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    print("🤖 Telegram Bot Running...")

    app.run_polling()


if __name__ == "__main__":
    main()