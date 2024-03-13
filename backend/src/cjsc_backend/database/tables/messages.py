#!/usr/bin/env python3
from loguru import logger
from psycopg2 import DatabaseError
from cjsc_backend.routers.http.schemas.user import UserLoginSchema, UserBaseSchema
from cjsc_backend.routers.http.schemas.message import Message


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


def get_chat_messages(conn, peer_1_id: int, peer_2_id: int, from_msg_id: int | None = None) -> list[Message]:
    """_summary_

    Args:
        conn (_type_): PostgreSQL connection object.
        peer_1_id (int): User ID of the first peer.
        peer_2_id (int): User ID of the second peer.
        from_msg_id (int | None, optional): Retrieve all messages starting from this Message ID. Defaults to None.

    Returns:
        list: List of messages between the two peers.
    """
    if peer_1_id == peer_2_id:
        raise ValueError("peer_1_id and peer_2_id must be different.")
    # Get all messages between from_user_id and to_user_id
    messages = []
    with conn.cursor() as curs:
        try:
            if not from_msg_id:
                curs.execute(
                    "SELECT id, from_user_id, to_user_id, is_read, content, created_at FROM messages WHERE (from_user_id = %s \
    AND to_user_id = %s) OR (from_user_id = %s AND to_user_id = %s)",
                    (peer_1_id, peer_2_id, peer_2_id, peer_1_id)
                )
                raw_messages = curs.fetchall()
                logger.debug(f"Got messages for chat between {peer_1_id} and {peer_2_id}: {messages}")
            else:
                curs.execute(
                    "SELECT id, from_user_id, to_user_id, is_read, content, created_at FROM messages WHERE ((from_user_id = %s \
    AND to_user_id = %s) OR (from_user_id = %s AND to_user_id = %s)) AND id >= %s",
                    (peer_1_id, peer_2_id, peer_2_id, peer_1_id, from_msg_id)
                )
                raw_messages = curs.fetchall()
                logger.debug(f"Got messages for chat between {peer_1_id} and {peer_2_id} ({from_msg_id=}): {messages}")
        except DatabaseError as e:
            logger.error(f"Failed to get chat messages: {e}")
            conn.rollback()
            raise e

    messages = []
    for msg in raw_messages:
        messages.append(Message(
            id=msg[0],
            from_user_id=msg[1],
            to_user_id=msg[2],
            is_read=msg[3],
            content=msg[4],
            created_at=msg[5]
        ))
    logger.debug(f"Returning messages: {messages}")

    return messages


def create_chat_message(conn, message: Message):
    """_summary_

    Args:
        conn (_type_): PostgreSQL connection object.
        message (Message): Message object to be inserted into the database.
    """
    with conn.cursor() as curs:
        try:
            curs.execute(
                "INSERT INTO messages (from_user_id, to_user_id, content) VALUES (%s, %s, %s)",
                (message.from_user_id, message.to_user_id, message.content)
            )
            conn.commit()
        except DatabaseError as e:
            logger.error(f"Failed to create chat message: {e}")
            conn.rollback()
            raise e
    return
