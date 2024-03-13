#!/usr/bin/env python3
from datetime import datetime
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
    logger.debug(f"Getting chats for user {user_id}")
    # List all chats (opposite users' ids) of user_id without repeating
    chats_raw = []
    with conn.cursor() as curs:
        try:
            curs.execute(
                "SELECT DISTINCT ON (from_user_id, to_user_id) from_user_id, to_user_id FROM messages WHERE from_user_id = %s OR to_user_id = %s",
                (user_id, user_id)
            )
            chats_raw = curs.fetchall()
        except DatabaseError as e:
            logger.error(f"Failed to get user chats: {e}")
            conn.rollback()
            raise e

    chats: set = set()
    for chat in chats_raw:
        if chat[0] == user_id:
            chats.add(chat[1])
        else:
            chats.add(chat[0])

    logger.debug(f"Found {len(chats)} chats for user {user_id}: {chats}")

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


def get_all_chat_messages(conn, user_id: int, from_msg_id: int | None = None) -> list[Message]:
    """Get all chat messages for a user.

    Args:
        conn (_type_): PostgreSQL connection object.
        user_id (int): User ID to get messages for.
        from_msg_id (int | None, optional): Retrieve all messages starting from this Message ID. Defaults to None.

    Returns:
        list[Message]: List of messages for the user.
    """
    messages = []
    with conn.cursor() as curs:
        try:
            if not from_msg_id:
                curs.execute(
                    "SELECT id, from_user_id, to_user_id, is_read, content, created_at FROM messages WHERE from_user_id = %s OR to_user_id = %s",
                    (user_id, user_id)
                )
                raw_messages = curs.fetchall()
            else:
                curs.execute(
                    "SELECT id, from_user_id, to_user_id, is_read, content, created_at FROM messages WHERE (from_user_id = %s OR to_user_id = %s) AND id >= %s",
                    (user_id, user_id, from_msg_id)
                )
                raw_messages = curs.fetchall()
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


def get_latest_message(conn, peer_1_id: int, peer_2_id: int) -> Message:
    """Get the latest message between two peers.

    Args:
        conn (_type_): PostgreSQL connection object.
        peer_1_id (int): User ID of the first peer.
        peer_2_id (int): User ID of the second peer.

    Returns:
        Message: Latest message between the two peers.
    """
    with conn.cursor() as curs:
        try:
            curs.execute(
                "SELECT id, from_user_id, to_user_id, is_read, content, created_at FROM messages WHERE (from_user_id = %s \
AND to_user_id = %s) OR (from_user_id = %s AND to_user_id = %s) ORDER BY created_at DESC LIMIT 1",
                (peer_1_id, peer_2_id, peer_2_id, peer_1_id)
            )
            latest_msg = curs.fetchone()
        except DatabaseError as e:
            logger.error(f"Failed to get latest message timestamp: {e}")
            conn.rollback()
            raise e

    return Message(
        id=latest_msg[0],
        from_user_id=latest_msg[1],
        to_user_id=latest_msg[2],
        is_read=latest_msg[3],
        content=latest_msg[4],
        created_at=latest_msg[5]
    )


def get_unread_count(conn, peer_checker_id: int, peer_sender_id: int):
    """Get the number of unread messages between two peers.

    Args:
        conn (_type_): PostgreSQL connection object.
        peer_1_id (int): User ID of the first peer.
        peer_2_id (int): User ID of the second peer.

    Returns:
        int: Number of unread messages between the two peers.
    """
    with conn.cursor() as curs:
        try:
            curs.execute(
                "SELECT COUNT(*) FROM messages WHERE from_user_id = %s AND to_user_id = %s AND is_read = FALSE",
                (peer_sender_id, peer_checker_id)
            )
            unread_count = curs.fetchone()
        except DatabaseError as e:
            logger.error(f"Failed to get unread message count: {e}")
            conn.rollback()
            raise e

    logger.debug(f"Got raw unread count for chat on checker ID {peer_checker_id} from sender ID {peer_sender_id}: {unread_count}")
    return unread_count[0]


def mark_as_read_message(conn, peer_receiver_id: int, peer_sender_id: int) -> None:
    """Mark all messages sent from peer_sender_id to peer_receiver_id as read.

    Args:
        conn (_type_): PostgreSQL connection object.
        peer_receiver_id (int): User ID of the receiver.
        peer_sender_id (int): User ID of the sender.

    Raises:
        DatabaseError: If the operation fails.
    """
    logger.debug(f"Marking messages as read that are sent from user ID {peer_sender_id} to user ID {peer_receiver_id}")
    with conn.cursor() as curs:
        try:
            curs.execute(
                "UPDATE messages SET is_read = TRUE WHERE from_user_id = %s AND to_user_id = %s",
                (peer_sender_id, peer_receiver_id)
            )
            logger.debug(f"Rows affected: {curs.rowcount}")
            conn.commit()
        except DatabaseError as e:
            logger.error(f"Failed to mark messages as read: {e}")
            conn.rollback()
            raise e
    return
