from fastapi import APIRouter, HTTPException

from app.schemas.user import (
    UserRegister,
    UserLogin,
    ForgotPasswordRequest
)

from app.services.user_service import (
    register_user,
    login_user
)

from app.auth.jwt_handler import create_access_token

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# ================= REGISTER =================

@router.post("/register")
def register(user: UserRegister):

    success = register_user(user)

    if not success:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    return {
        "success": True,
        "message": "Registration Successful"
    }


# ================= LOGIN =================

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
        "success": True,
        "access_token": token,
        "token_type": "bearer",
        "email": db_user.email,
        "role": db_user.role
    }


# ================= FORGOT PASSWORD =================

@router.post("/forgot-password")
def forgot_password(data: ForgotPasswordRequest):

    """
    Temporary endpoint.

    Later this will:
    - generate reset token
    - send email
    - allow password reset
    """

    return {
        "success": True,
        "message": f"If an account exists for {data.email}, a password reset link will be sent."
    }
