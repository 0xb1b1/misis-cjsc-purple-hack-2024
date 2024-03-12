#!/usr/bin/env python3
from pydantic import BaseModel, EmailStr
from datetime import datetime


class UserBaseSchema(BaseModel):
    id: int
    email: EmailStr
    password_hash: str
    avatar_url: str | None = None
    role: str = "user"
    first_name: str
    last_name: str | None = None
    created_at: datetime | None = None


class UserSignupSchema(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str | None = None
    created_at: datetime = datetime.now()


class UserResponseSchema(UserBaseSchema):
    login_successful: bool | None


class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str


class UserInfoSchema(BaseModel):
    id: int
    email: EmailStr
    role: str
