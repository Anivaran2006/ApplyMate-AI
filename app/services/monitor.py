from app.scraper.nta_scraper import get_latest_notification
from app.database.db_manager import load_data, save_data
from app.services.logger import logger

from app.services.pdf_service import extract_pdf_text
from app.services.summary_service import create_summary
from app.services.category_service import detect_category
from app.services.user_service import get_matching_users

from app.notifier.email_notifier import send_email


def monitor():

    print("Scheduler Triggered")

    logger.info("Checking NTA Website")

    notification = get_latest_notification()

    title = notification["title"]

    data = load_data()

    if title not in data["seen_notifications"]:

        logger.info("New Notification Found")

        pdf_url = notification["link"]

        text = extract_pdf_text(pdf_url)

        summary = create_summary(text)

        category = detect_category(summary)

        users = get_matching_users(category)

        print("Category:", category)

        print("Users:", users)

        for user in users:

            send_email(
                title,
                summary,
                user["email"]
            )

            print(
                "Email sent to:",
                user["email"]
            )

        data["seen_notifications"].append(title)

        save_data(data)

        return {
            "status": "NEW_NOTIFICATION",
            "notification": notification
        }

    return {
        "status": "ALREADY_SEEN",
        "notification": notification
    }