from typing import List

from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):

    email: EmailStr

    password: str

    categories: List[str] = Field(
        default_factory=lambda: ["GENERAL"]
    )


class UserLogin(BaseModel):

    email: EmailStr

    password: str


# ================= FORGOT PASSWORD =================

class ForgotPasswordRequest(BaseModel):

    email: EmailStr