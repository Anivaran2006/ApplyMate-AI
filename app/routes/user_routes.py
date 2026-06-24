from fastapi import APIRouter

from app.schemas.user import User

from app.services.user_service import (
    add_user,
    get_users,
    delete_user,
    update_user_category
)

from app.notifier.email_notifier import send_email

router = APIRouter()


@router.post("/register")
def register_user(user: User):

    added = add_user(
        user.dict()
    )

    if not added:

        return {
            "message": "User already exists"
        }

    send_email(
        "Welcome to ApplyMate AI",
        f"""
        <h2>Welcome to ApplyMate AI</h2>
        <p>You have successfully subscribed for {user.category} notifications.</p>
        """,
        user.email
    )

    return {
        "message": "User Registered"
    }


@router.get("/users")
def list_users():

    return get_users()


@router.put("/users/{email}")
def update_category(
    email: str,
    category: str
):

    updated = update_user_category(
        email,
        category
    )

    if not updated:

        return {
            "message": "User not found"
        }

    return {
        "message": "Category updated"
    }


@router.delete("/users/{email}/{category}")
def remove_user(
    email: str,
    category: str
):

    delete_user(
        email,
        category
    )

    return {
        "message": "User removed"
    }