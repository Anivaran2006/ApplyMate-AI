from pydantic import BaseModel, EmailStr


class UserRegister(BaseModel):

    email: EmailStr

    password: str

    category: str = "GENERAL"


class UserLogin(BaseModel):

    email: EmailStr

    password: str