#!/usr/bin/env python3
from loguru import logger
from psycopg2 import DatabaseError
from cjsc_backend.routers.http.schemas.user import UserLoginSchema, UserBaseSchema
from cjsc_backend.routers.http.schemas.message import Message
from cjsc_backend.routers.http.schemas.chat_session import ChatSession
from cjsc_backend.database.tables import messages as db_msgs

# CREATE TABLE IF NOT EXISTS chat_sessions (
#   id SERIAL PRIMARY KEY,
#   user_1_id INTEGER NOT NULL REFERENCES users(id),
#   user_2_id INTEGER NOT NULL REFERENCES users(id),
#   allow_ml BOOLEAN NOT NULL DEFAULT TRUE,
#   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# )


def get_latest_chat_session(conn, message: Message) -> ChatSession:
    ...


def _is_latest_session_expired(conn, peer_1_id, peer_2_id) -> bool:
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
ORDER BY created_at DESC LIMIT 1",
                (peer_1_id, peer_2_id, peer_2_id, peer_1_id),
            )
            last_session = curs.fetchone()
        except DatabaseError as e:
            logger.error(f"Failed to get last session: {e}")
            conn.rollback()
            raise e

    if last_session is None:
        return True

    last_session = last_session[0]
    return last_session < datetime.now() - timedelta(minutes=30)