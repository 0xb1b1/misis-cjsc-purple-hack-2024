#!/usr/bin/env python3
from loguru import logger
from psycopg2 import DatabaseError
from cjsc_backend.routers.http.schemas.user import UserLoginSchema, UserBaseSchema


# CREATE TABLE IF NOT EXISTS messages (
#   id SERIAL PRIMARY KEY,
#   from_user_id INTEGER NOT NULL REFERENCES users(id),
#   to_user_id INTEGER NOT NULL REFERENCES users(id),
#   is_read BOOLEAN NOT NULL DEFAULT FALSE,
#   content TEXT NOT NULL,
#   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );

def get_user_chats(conn, user_id: int) -> list[int]:
    # List all chats (opposite users' ids) of user_id without repeating
    chats = []
    with conn.cursor() as curs:
        try:
            curs.execute(
                "SELECT DISTINCT ON (from_user_id, to_user_id) from_user_id, to_user_id FROM messages WHERE from_user_id = %s OR to_user_id = %s",
                (user_id, user_id)
            )
            chats = curs.fetchall()
        except DatabaseError as e:
            logger.error(f"Failed to get user chats: {e}")
            conn.rollback()
            raise e

    return list(chats)


def get_chat_messages(conn, from_user_id: int, to_user_id: int) -> list:
    # Get all messages between from_user_id and to_user_id
    messages = []
    with conn.cursor() as curs:
        try:
            curs.execute(
                "SELECT * FROM messages WHERE (from_user_id = %s \
AND to_user_id = %s) OR (from_user_id = %s AND to_user_id = %s)",
                (from_user_id, to_user_id, to_user_id, from_user_id)
            )
            messages = curs.fetchall()
        except DatabaseError as e:
            logger.error(f"Failed to get chat messages: {e}")
            conn.rollback()
            raise e

    return messages
