import secrets

from sqlalchemy.orm import Session

from app.database.models import User


def generate_telegram_token(db: Session, user_id: int):
    """
    Generate a unique Telegram linking token for a user.
    """

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        return None

    token = secrets.token_urlsafe(32)

    user.telegram_link_token = token

    db.commit()
    db.refresh(user)

    return token


def get_user_by_token(db: Session, token: str):
    """
    Find a user by Telegram link token.
    """

    return (
        db.query(User)
        .filter(User.telegram_link_token == token)
        .first()
    )


def connect_telegram_account(
    db: Session,
    token: str,
    chat_id: str
):
    """
    Link Telegram chat ID with the user.
    """

    user = get_user_by_token(db, token)

    if not user:
        return None

    user.telegram_chat_id = str(chat_id)

    # Remove token after successful linking
    user.telegram_link_token = None

    db.commit()
    db.refresh(user)

    return user


def disconnect_telegram(db: Session, user_id: int):
    """
    Disconnect Telegram account.
    """

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        return False

    user.telegram_chat_id = None
    user.telegram_link_token = None

    db.commit()

    return True