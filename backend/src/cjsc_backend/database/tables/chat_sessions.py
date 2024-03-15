#!/usr/bin/env python3
from datetime import datetime, timedelta

from cjsc_backend import config
from cjsc_backend.database.tables import messages as db_msgs

# from cjsc_backend.routers.http.schemas.user import \
#     UserLoginSchema, UserBaseSchema
# from cjsc_backend.routers.http.schemas.message import Message
from cjsc_backend.routers.http.schemas.chat_session import ChatSession
from loguru import logger
from psycopg2 import DatabaseError

# CREATE TABLE IF NOT EXISTS chat_sessions (
#   id SERIAL PRIMARY KEY,
#   user_1_id INTEGER NOT NULL REFERENCES users(id),
#   user_2_id INTEGER NOT NULL REFERENCES users(id),
#   allow_ml BOOLEAN NOT NULL DEFAULT TRUE,
#   allow_faq BOOLEAN NOT NULL DEFAULT TRUE,
#   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# )


def get_latest_chat_session(conn, peer_1_id, peer_2_id) -> ChatSession:
    """Get the latest chat session between two users.
    If the chat session is expired, create a new one.

    Args:
        conn (_type_): PostgreSQL connection object.
        peer_1_id (_type_): User ID of the first peer.
        peer_2_id (_type_): User ID of the second peer.

    Returns:
        ChatSession: ChatSession object.
    """
    if is_latest_session_expired(conn, peer_1_id, peer_2_id):
        create_chat_session(conn, peer_1_id, peer_2_id)

    with conn.cursor() as curs:
        try:
            curs.execute(
                "SELECT id, user_1_id, user_2_id, allow_ml, created_at FROM chat_sessions WHERE \
(user_1_id = %s AND user_2_id = %s) OR (user_1_id = %s AND user_2_id = %s) \
ORDER BY id DESC LIMIT 1",
                (peer_1_id, peer_2_id, peer_2_id, peer_1_id),
            )
            last_session = curs.fetchone()
        except DatabaseError as e:
            logger.error(f"Failed to get last session: {e}")
            conn.rollback()
            raise e

    if last_session is None:
        raise ValueError("No chat session found. This should not be possible.")

    return ChatSession(
        id=last_session[0],
        user_1_id=last_session[1],
        user_2_id=last_session[2],
        allow_ml=last_session[3],
        created_at=last_session[4],
    )


def create_chat_session(conn, peer_1_id, peer_2_id) -> None:
    """Create a new chat session between two users.

    Args:
        conn (_type_): PostgreSQL connection object.
        peer_1_id (_type_): User ID of the first peer.
        peer_2_id (_type_): User ID of the second peer.
    """
    with conn.cursor() as curs:
        try:
            curs.execute(
                "INSERT INTO chat_sessions (user_1_id, user_2_id, created_at) \
VALUES (%s, %s, CURRENT_TIMESTAMP)",
                (peer_1_id, peer_2_id),
            )
            conn.commit()
        except DatabaseError as e:
            logger.error(f"Failed to create chat session: {e}")
            conn.rollback()
            raise e


def is_latest_session_expired(conn, peer_1_id, peer_2_id) -> bool:
    """Check if the last session stored in the database is expired.

    Args:
        conn (_type_): PostgreSQL connection object.
        peer_1_id (_type_): User ID of the first peer.
        peer_2_id (_type_): User ID of the second peer.

    Returns:
        bool: True if the last session is expired, False otherwise.
    """
    with conn.cursor() as curs:
        try:
            curs.execute(
                "SELECT created_at FROM chat_sessions WHERE \
(user_1_id = %s AND user_2_id = %s) OR (user_1_id = %s AND user_2_id = %s) \
ORDER BY id DESC LIMIT 1",
                (peer_1_id, peer_2_id, peer_2_id, peer_1_id),
            )
            last_session = curs.fetchone()
        except DatabaseError as e:
            logger.error(f"Failed to get last session: {e}")
            conn.rollback()
            raise e

    if last_session is None:
        return True

    try:
        last_message = db_msgs.get_latest_message(conn, peer_1_id, peer_2_id)
    except TypeError:  # No messages found
        return True

    return last_message.created_at < datetime.now() - timedelta(
        hours=config.CHAT_EXPIRY_MINUTES
    )


def set_allow_ml(conn, peer_1_id: int, peer_2_id: int, allow_ml: bool) -> None:
    """Set the allow_ml flag for a chat session.

    Args:
        conn (_type_): PostgreSQL connection object.
        peer_1_id (_type_): User ID of the first peer.
        peer_2_id (_type_): User ID of the second peer.
        allow_ml (_type_): New value for the allow_ml flag.
    """
    session = get_latest_chat_session(conn, peer_1_id, peer_2_id)
    with conn.cursor() as curs:
        try:
            curs.execute(
                "UPDATE chat_sessions SET allow_ml = %s WHERE id = %s",
                (allow_ml, session.id),
            )
            conn.commit()
        except DatabaseError as e:
            logger.error(f"Failed to set allow_ml: {e}")
            conn.rollback()
            raise e
