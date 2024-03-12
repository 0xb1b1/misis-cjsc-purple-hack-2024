#!/usr/bin/env python3
from loguru import logger
from psycopg2 import DatabaseError
from cjsc_backend.routers.http.schemas.user import UserLoginSchema, UserBaseSchema


def get(conn, uid: int | None = None, email: str | None = None) -> str:
    if not uid and not email:
        logger.error("No user identifier provided")
        return None

    if uid:
        return _get_by_uid(conn, uid)
    elif email:
        return _get_by_email(conn, email)


def create(conn, user: UserBaseSchema) -> str:
    logger.debug(f"Creating user: {user.email}")
    with conn.cursor() as curs:
        try:
            curs.execute(
                "INSERT INTO users (email, password_hash, avatar_url, role, \
first_name, last_name, created_at) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (
                    user.email,
                    user.password_hash,
                    user.avatar_url,
                    user.role,
                    user.first_name,
                    user.last_name,
                    user.created_at,
                ),
            )
            conn.commit()
        except DatabaseError as e:
            logger.error(f"Failed to create user, rolling back: {e}")
            curs.rollback()
            raise e


def _get_by_email(conn, email: str) -> str:
    with conn.cursor() as curs:
        try:
            curs.execute("SELECT id, email, password_hash, avatar_url, role, \
first_name, last_name, created_at FROM users WHERE email = %s", (email,))
            user = curs.fetchone()
        except DatabaseError as e:
            logger.error(f"Failed to get user by email, rolling back: {e}")
            curs.rollback()
            raise e

    return UserBaseSchema(
        id=user[0],
        email=user[1],
        password_hash=user[2],
        avatar_url=user[3],
        role=user[3],
        first_name=user[4],
        last_name=user[5],
    )


def _get_by_uid(conn, uid: int) -> str:
    return None
