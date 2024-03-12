#!/usr/bin/env python3
from datetime import datetime

from cjsc_backend.routers.http.schemas.user import UserSignupSchema
from cjsc_backend.models.user import User


def user_signup_schema(
    schema: UserSignupSchema
) -> User:
    return User(
        email=schema.email,
        password_hash=schema.password_hash,
        role="user",
        first_name=schema.first_name,
        last_name=schema.last_name,
        created_at=datetime.utcnow(),
    )
