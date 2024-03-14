#!/usr/bin/env python3
from fastapi import APIRouter, Security, HTTPException
from fastapi_jwt import JwtAuthorizationCredentials
from loguru import logger
from datetime import datetime
from psycopg2 import DatabaseError
from cjsc_backend import config
from cjsc_backend.database.tables import messages as db_msgs
from cjsc_backend.database.tables import users as db_users
from cjsc_backend.database.connect import create_connection_with_config
from cjsc_backend.routers.http.schemas.token import TokenSchema
# from cjsc_backend.routers.http.schemas.user import UserBaseSchema, \
#     UserLoginSchema, UserInfoSchema, UserSignupSchema
from cjsc_backend.routers.http.schemas.user import UserChatEntriesSchema, \
    UserChatEntrySchema
from cjsc_backend.routers.http.schemas.message import Message

# See https://fastapi.tiangolo.com/tutorial/bigger-applications/

db = create_connection_with_config()

router = APIRouter(
    prefix="/msg",
    tags=['Messages', ],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}}
)


@router.get(
    "/chats",
)
async def messages_get_chats(
    credentials: JwtAuthorizationCredentials = Security(
        config.jwt_ac,
    ),
) -> UserChatEntriesSchema:
    logger.debug(
        f"Getting chats for user {credentials["id"]}"
    )

    my_user = db_users.get(db, uid=credentials["id"])

    try:
        chats = db_msgs.get_user_chats(db, credentials["id"])
    except DatabaseError as e:
        logger.error(f"Failed to get user chats: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get user chats",
        )

    users = {}
    for chat in chats:
        latest_message = db_msgs.get_latest_message(
            db,
            credentials["id"],
            chat,
        )
        logger.debug(f"Getting info about user {chat}")
        user_info = db_users.get(db, uid=chat)
        users[chat] = UserChatEntrySchema(
            id=user_info.id,
            first_name=user_info.first_name,
            last_name=user_info.last_name,
            avatar_url=user_info.avatar_url,
            unread_count=db_msgs.get_unread_count(db, chat, my_user.id),
            last_message_content=latest_message.content,
            last_message_created_at=datetime.strftime(latest_message.created_at, "%Y-%m-%d %H:%M:%S"),
        )

    return {
        "chats": chats,
        "users": users,
        "is_operator": db_users.is_operator(db, credentials["id"])
    }


# Intended for ML functionality
@router.post(
    "/send",
)
async def messages_send(ca_secret: str, msg: Message):
    """This method is intended to be used by the ML part of the system.
    Send a message object with **correctly configured** `from_user_id`
    and `to_user_id` fields to send a message. `from_user_id` should
    always be `0`, so a 4XX error will be thrown if this is not the case.

    Args:
        ca_secret (str): Cross-app secret between ML and the backend. Will throw 403 if incorrect.
        msg (Message): Message object to send.
    """
    logger.debug(f"Received message from ML: {msg}")
    if ca_secret != config.CROSS_APP_SECRET:
        logger.debug(f"Received incorrect cross-app secret: {ca_secret}")
        raise HTTPException(
            status_code=403,
            detail="Incorrect cross-app secret",
        )

    if msg.from_user_id != 0:
        logger.warning(f"Received message with incorrect from_user_id: {msg.from_user_id}")
        raise HTTPException(
            status_code=400,
            detail="from_user_id must be 0",
        )

    if msg.to_user_id == 0:
        logger.warning(f"Received message with incorrect to_user_id: {msg.to_user_id}")
        raise HTTPException(
            status_code=400,
            detail="to_user_id must not be 0",
        )

    logger.debug(f"Sending message: {msg}")
    # Websocket clients will receive this message after ws/messages.py scans it
    db_msgs.create_chat_message(db, msg)
    logger.debug(f"Message sent: {msg}")
    return {
        "status": "ok",
    }


async def get_user_info():
    pass
