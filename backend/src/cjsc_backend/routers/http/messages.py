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


async def get_user_info():
    pass
