#!/usr/bin/env python3
import asyncio
from datetime import datetime

import socketio
from cjsc_backend import config
from cjsc_backend.connectors import ml
from cjsc_backend.database.connect import create_connection_with_config
from cjsc_backend.database.tables import chat_sessions, messages
from cjsc_backend.routers.http.schemas.message import Message
from fastapi import APIRouter
from jose import jwt
from jose.jwt import ExpiredSignatureError, JWTError
from loguru import logger
from psycopg2 import DatabaseError
from socketio.exceptions import TimeoutError

router = APIRouter(
    tags=["Websockets"],
    prefix="/ws/messages",
)

db = create_connection_with_config()

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")


@sio.on(event="auth", namespace="/webapp")
async def auth(sid, token):
    logger.debug(f"Authenticating user with token: {token} (sid: {sid})")

    try:
        user = jwt.decode(token, key=config.JWT_SECRET_KEY, algorithms=["HS256"])
    except JWTError as e:
        logger.debug(f"Failed to authenticate user: {e}")
        await sio.emit("auth", data="error", room=sid, namespace="/webapp")
        return
    except ExpiredSignatureError as e:
        logger.debug(f"User's token expired: {e}")
        await sio.emit("auth", data="expired", room=sid, namespace="/webapp")
        return

    logger.debug(f"Authenticated user: {user}")

    await sio.emit(
        "auth",
        data={
            "status": "ok",
            "user": {"id": user["subject"]["id"], "email": user["subject"]["email"]},
        },
        room=sid,
        namespace="/webapp",
    )
    logger.debug(f"Saving session for {sid}")
    await sio.save_session(sid, {"user": user}, namespace="/webapp")
    logger.debug(
        f"Saved session for {sid}: {await sio.get_session(sid, namespace='/webapp')}"
    )


@sio.on(event="chats_list", namespace="/webapp")
async def chats_list(sid):
    """Sends all chats of the user to the client (recipients' user IDs).
    Returns data in the following format:
    ```
    [
        'chats_list',
        {
            'chats': [
                0, 2, 4
            ]
        }
    ]
    ```

    Args:
        sid (_type_): Socket ID. Autopopulated on request by SocketIO Client.
    """
    logger.debug(f"Getting chats for {sid}")
    my_user = await sio.get_session(sid, namespace="/webapp")
    my_user_id = my_user["user"]["subject"]["id"]

    try:
        chats = messages.get_user_chats(db, my_user_id)
    except DatabaseError as e:
        logger.error(f"Failed to get user chats: {e}")
        await sio.emit(
            "chats_list",
            data={"error": "Failed to get user chats", "info: ": str(e)},
            room=sid,
            namespace="/webapp",
        )
        return

    await sio.emit("chats_list", data={"chats": chats}, room=sid, namespace="/webapp")


@sio.on(event="chat_listen", namespace="/webapp")
async def chat_listen(sid, user_id):
    """Sends all updates from the chat with user_id to the client, including the initiator's messages.
    Messages from this event handler are in the following format:
    ```
        [
            'chat_message',
            {
                'message': {
                    'id': 24,
                    'from': 1,
                    'to': 4,
                    'content': 'Hi there! This is a message lmao uwu',
                    'created_at': '2024-03-13 19:22:05'
                }
            }
        ]
    ```

    Args:
        sid (_type_): Socket ID. Autopopulated on request by SocketIO Client.
        user_id (_type_): User ID that the client wants to listen for messages from.
    """
    # the user_id is taken from the database, not a room
    logger.debug(f"User {user_id} is listening for new messages (sid: {sid})")

    # get the user's dialog with the user_id
    my_user = await sio.get_session(sid, namespace="/webapp")
    my_user_id = my_user["user"]["subject"]["id"]

    last_msg_id = None
    # Send all messages
    heartbeat_counter = 1
    while True:
        try:
            if heartbeat_counter % 10 == 0:
                logger.debug(f"Calling heartbeat for {sid}")
                await sio.call(
                    "heartbeat",
                    data="heartbeat",
                    to=sid,
                    namespace="/webapp",
                    timeout=5,
                )
                heartbeat_counter = 1
            heartbeat_counter += 1
        except TimeoutError:
            logger.error(
                f"Failed to send heartbeat to {sid}; client probably disconnected"
            )
            await sio.disconnect(sid, namespace="/webapp")
            return

        # Send messages
        try:
            msgs = messages.get_chat_messages(db, my_user_id, user_id, last_msg_id)
            last_msg_id = msgs[-1].id + 1 if len(msgs) > 0 else last_msg_id
            for msg in msgs:
                await sio.call(
                    "chat_message",
                    data={
                        "message": {
                            "id": msg.id,
                            "from": msg.from_user_id,
                            "to": msg.to_user_id,
                            "content": msg.content,
                            "created_at": datetime.strftime(
                                msg.created_at, "%Y-%m-%d %H:%M:%S"
                            ),
                        }
                    },
                    to=sid,
                    namespace="/webapp",
                    timeout=5,
                )
        except DatabaseError as e:
            logger.error(f"Failed to get chat messages (database): {e}")
            # disconnect client on exception (and send error message)
            await sio.emit(
                "chat_message",
                data={"error": "Failed to get chat messages", "info: ": str(e)},
                room=sid,
                namespace="/webapp",
            )
            await sio.disconnect(sid, namespace="/webapp")
            return
        # IMPORTANT: Do not spam TODO: check the sleep duration performance
        await asyncio.sleep(0.5)


@sio.on("chats_listen", namespace="/webapp")
async def chats_listen(sid):
    """Sends all updates (from ALL CHATS) to the client, including the initiator's messages.
    Messages from this event handler are in the following format:
    ```
        [
            'chat_message',
            {
                'message': {
                    'id': 24,
                    'from': 1,
                    'to': 4,
                    'content': 'Hi there! This is a message lmao uwu',
                    'created_at': '2024-03-13 19:22:05'
                }
            }
        ]
    ```

    Args:
        sid (_type_): Socket ID. Autopopulated on request by SocketIO Client.
    """
    # Same as chat_listen, but for all chats of the user
    # the user_id is taken from the database, not a room
    logger.debug(f"User is listening for new chats (sid: {sid})")

    my_user = await sio.get_session(sid, namespace="/webapp")
    await asyncio.sleep(0.5)
    logger.debug(f"Got user from SIO: {my_user}")
    my_user_id = my_user["user"]["subject"]["id"]

    last_msg_id = None
    # Send all messages
    while True:
        # Send messages
        try:
            logger.debug(f"Getting chat messages for {my_user_id} from {last_msg_id}")
            msgs = messages.get_all_chat_messages(db, my_user_id, last_msg_id)
            for msg in msgs:
                logger.debug(
                    f"Sending message to {sid}: {msg.content} from {msg.from_user_id} to {msg.to_user_id} at {msg.created_at}"
                )
                await sio.emit(  # TODO: change back after testing
                    "chat_message",
                    data={
                        "message": {
                            "id": msg.id,
                            "from": msg.from_user_id,
                            "to": msg.to_user_id,
                            "content": msg.content,
                            "created_at": datetime.strftime(
                                msg.created_at, "%Y-%m-%d %H:%M:%S"
                            ),
                        }
                    },
                    to=sid,
                    namespace="/webapp",
                    # timeout=5
                )
            last_msg_id = msgs[-1].id + 1 if len(msgs) > 0 else last_msg_id

            # Mark messages sent by all users that communicate with the user as read
            for msg in msgs:
                if msg.to_user_id == my_user_id:
                    messages.mark_as_read_message(db, my_user_id, msg.id)

        except DatabaseError as e:
            logger.error(f"Failed to get chat messages (database): {e}")
            # disconnect client on exception (and send error message)
            await sio.emit(
                "chat_message",
                data={"error": "Failed to get chat messages", "info: ": str(e)},
                room=sid,
                namespace="/webapp",
            )
            await sio.disconnect(sid, namespace="/webapp")
            return

        except TimeoutError:
            logger.error(
                f"Failed to send chat messages to {sid}; client probably disconnected"
            )
            await sio.disconnect(sid, namespace="/webapp")
            return
        # IMPORTANT: Do not spam TODO: check the sleep duration performance
        await asyncio.sleep(0.5)


@sio.on(event="chat_send", namespace="/webapp")
async def chat_send(sid, message):
    """Receives a message from the client and saves it to the database, then sends to the recipient using Websockets.

    Args:
        sid (_type_): Socket ID. Autopopulated on request by SocketIO Client.
        message (_type_): Message object in the following format: `{"message": {"to": 4, "content": f"send_msg_counter: {send_msg_counter}"}}`
    """
    # Receive messages from SIO client
    logger.debug(f"Received chat message from {sid}: {message}")
    my_user = await sio.get_session(sid, namespace="/webapp")
    await asyncio.sleep(0.5)
    my_user_id = my_user["user"]["subject"]["id"]

    if "message" not in message:
        logger.debug(
            f"Received chat message from {sid} without message: {message}; skipping."
        )
        return

    logger.debug(f"Received chat message from {sid}: {message['message']}")
    msg_raw = message["message"]
    msg = Message(
        from_user_id=my_user_id,
        to_user_id=msg_raw["to"],
        content=msg_raw["content"],
        created_at=datetime.now(),
    )
    if msg.from_user_id != my_user_id:
        logger.warn(f"Received message from wrong user: {msg}")
        await sio.emit(
            "chat_message",
            data={"error": "Received message from wrong user", "info: ": str(msg)},
            room=sid,
            namespace="/webapp",
        )
        return
    try:
        messages.create_chat_message(db, msg)
    except DatabaseError as e:
        logger.error(f"Failed to save chat message: {e}")
        await sio.emit(
            "chat_message",
            data={"error": "Failed to save chat message", "info: ": str(e)},
            room=sid,
            namespace="/webapp",
        )
        return

    # Check if user wishes to talk to a live person; if so, turn off ML
    msg_lcontent = msg.content.lower()
    if "оператор" in msg_lcontent or (
        "человек" in msg_lcontent and len(msg_lcontent) < 12
    ):
        logger.debug(
            f"User {my_user_id} wants to talk to a live person. Turning off ML for this session."
        )
        chat_sessions.set_allow_ml(db, my_user_id, msg.to_user_id, False)

    session = chat_sessions.get_latest_chat_session(db, my_user_id, msg.to_user_id)
    if session is None:
        logger.warning(
            f"Chat session not found for users {my_user_id} and {msg.to_user_id}. Creating a new one."
        )
        chat_sessions.create_chat_session(db, my_user_id, msg.to_user_id)
        session = chat_sessions.get_latest_chat_session(db, my_user_id, msg.to_user_id)

    if session.allow_ml:
        logger.debug(f"ML is allowed for this session. Querying ML for message: {msg}")
        ml.query(msg)


@sio.on("disconnect")
async def disconnect(sid):
    logger.debug(f"Disconnecting {sid}")
    # remove the user from the session and stop listening for messages
    await sio.leave_room(sid, namespace="/webapp")
    await sio.save_session(sid, {"user": None}, namespace="/webapp")
