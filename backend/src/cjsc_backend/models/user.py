#!/usr/bin/env python3
from pydantic import BaseModel, EmailStr
from datetime import datetime


class User(BaseModel):
    id: int | None = None
    email: EmailStr
    password_hash: str
    role: str
    first_name: str
    last_name: str | None = None
    created_at: datetime | None = None
