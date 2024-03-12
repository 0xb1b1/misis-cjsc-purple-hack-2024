#!/usr/bin/env python3
from loguru import logger
from psycopg2 import DatabaseError
from cjsc_backend.models.user import User


def get(conn, uid: int | None = None, email: str | None = None) -> str:
    if not uid and not email:
        logger.error("No user identifier provided")
        return None

    if uid:
        return _get_by_uid(conn, uid)
    elif email:
        return _get_by_email(conn, email)


def _get_by_email(conn, email: str) -> str:
    with conn.cursor() as curs:
        try:
            curs.execute("SELECT id, email, password_hash, role, \
first_name, last_name, created_at FROM users WHERE email = ?", (email,))
            user = curs.fetchone()
        except DatabaseError as e:
            logger.error(f"Failed to get user by email: {e}")
            return None

    return User(
        id=user[0],
        email=user[1],
        password_hash=user[2],
        role=user[3],
        first_name=user[4],
        last_name=user[5],
        created_at=user[6],
    )


def _get_by_uid(conn, uid: int) -> str:
    return None
