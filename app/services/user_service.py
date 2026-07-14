from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.database.models import User, Subscription

from app.auth.security import (
    hash_password,
    verify_password
)


def register_user(data):

    db: Session = SessionLocal()

    try:

        existing = (
            db.query(User)
            .filter(User.email == data.email)
            .first()
        )

        if existing:
            return False

        default_category = (
            data.categories[0]
            if data.categories
            else "GENERAL"
        )

        new_user = User(

            email=data.email,

            password=hash_password(
                data.password
            ),

            # Temporary compatibility
            category=default_category

        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        # Save all selected categories

        for category in data.categories:

            subscription = Subscription(

                user_id=new_user.id,

                category=category

            )

            db.add(subscription)

        db.commit()

        return True

    finally:

        db.close()


def login_user(email, password):

    db: Session = SessionLocal()

    try:

        user = (
            db.query(User)
            .filter(User.email == email)
            .first()
        )

        if not user:
            return None

        if not verify_password(
            password,
            user.password
        ):
            return None

        return user

    finally:

        db.close()