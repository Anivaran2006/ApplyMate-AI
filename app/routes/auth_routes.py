from fastapi import APIRouter, HTTPException

from app.schemas.user import UserRegister, UserLogin

from app.services.user_service import (
    register_user,
    login_user
)

from app.auth.jwt_handler import create_access_token

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/register")
def register(user: UserRegister):

    success = register_user(user)

    if not success:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    return {
        "message": "Registration Successful"
    }


@router.post("/login")
def login(user: UserLogin):

    db_user = login_user(
        user.email,
        user.password
    )

    if not db_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid Email or Password"
        )

    token = create_access_token(
        {
            "sub": db_user.email,
            "role": db_user.role
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "email": db_user.email,
        "role": db_user.role
    }




