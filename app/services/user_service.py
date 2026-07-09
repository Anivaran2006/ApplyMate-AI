from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.database.models import User

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

        new_user = User(

            email=data.email,

            password=hash_password(
                data.password
            ),

            category=data.category

        )

        db.add(new_user)

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

        print("=================================")
        print("User from DB:", user)

        if not user:
            print("❌ User not found")
            return None

        print("Entered Password:", password)
        print("Stored Hash:", user.password)

        result = verify_password(password, user.password)

        print("Password Match:", result)
        print("=================================")

        if not result:
            return None

        return user

    finally:
        db.close()