#!/usr/bin/env python3
from datetime import datetime
import bcrypt
from loguru import logger
from psycopg2 import DatabaseError
from cjsc_backend.routers.http.schemas.user import UserLoginSchema, UserBaseSchema, UserSignupSchema


def get(conn, uid: int | None = None, email: str | None = None) -> UserBaseSchema:
    logger.debug(f"Getting user by uid: {uid} or email: {email}")
    if uid is not None:
        return _get_by_uid(conn, uid)
    elif email is not None:
        return _get_by_email(conn, email)
    else:
        raise ValueError("Must provide either uid or email")


def create(conn, user: UserSignupSchema) -> str:
    logger.debug(f"Creating user: {user.email}")
    with conn.cursor() as curs:
        try:
            curs.execute(
                "INSERT INTO users (email, password_hash, avatar_url, role, \
first_name, last_name, created_at) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (
                    user.email,
                    bcrypt.hashpw(
                        user.password.encode('utf-8'),
                        bcrypt.gensalt()
                    ).decode('utf-8'),
                    None,
                    "user",
                    user.first_name,
                    user.last_name,
                    datetime.now(),
                ),
            )
            conn.commit()
        except DatabaseError as e:
            logger.error(f"Failed to create user, rolling back: {e}")
            conn.rollback()
            raise e


def _get_by_email(conn, email: str) -> UserBaseSchema:
    with conn.cursor() as curs:
        try:
            curs.execute("SELECT id, email, password_hash, avatar_url, role, \
first_name, last_name, created_at FROM users WHERE email = %s", (email,))
            user = curs.fetchone()
        except DatabaseError as e:
            logger.error(f"Failed to get user by email, rolling back: {e}")
            conn.rollback()
            raise e

    if user is None:
        raise ValueError(f"User with email {email} not found")

    return UserBaseSchema(
        id=user[0],
        email=user[1],
        password_hash=user[2],
        avatar_url=user[3],
        role=user[4],
        first_name=user[5],
        last_name=user[6],
        # 2024-03-12T23:02:18.777335
        created_at=user[7],
    )


def _get_by_uid(conn, uid: int) -> UserBaseSchema:
    with conn.cursor() as curs:
        try:
            curs.execute("SELECT id, email, password_hash, avatar_url, role, \
first_name, last_name, created_at FROM users WHERE id = %s", (uid,))
            user = curs.fetchone()
        except DatabaseError as e:
            logger.error(f"Failed to get user by uid, rolling back: {e}")
            conn.rollback()
            raise e

    if user is None:
        raise ValueError(f"User with uid {uid} not found")

    return UserBaseSchema(
        id=user[0],
        email=user[1],
        password_hash=user[2],
        avatar_url=user[3],
        role=user[4],
        first_name=user[5],
        last_name=user[6],
        created_at=user[7],
    )


def is_operator(conn, uid: int) -> bool:
    with conn.cursor() as curs:
        try:
            curs.execute("SELECT role FROM users WHERE id = %s", (uid,))
            role = curs.fetchone()
        except DatabaseError as e:
            logger.error(f"Failed to get user role, rolling back: {e}")
            conn.rollback()
            raise e

    return role[0] == "operator"
