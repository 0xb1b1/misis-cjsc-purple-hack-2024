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


class UserResponseSchema(UserBaseSchema):
    login_successful: bool | None


class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str


class UserInfoSchema(BaseModel):
    email: EmailStr
    role: str
