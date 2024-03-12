#!/usr/bin/env python3
from pydantic import BaseModel, EmailStr


class UserBaseSchema(BaseModel):
    email: EmailStr
    password_hash: str
    first_name: str
    last_name: str | None = None


class UserSignupSchema(UserBaseSchema):
    ...


class UserResponseSchema(UserBaseSchema):
    login_successful: bool | None


class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str


class UserInfoSchema(BaseModel):
    email: EmailStr
    role: str
