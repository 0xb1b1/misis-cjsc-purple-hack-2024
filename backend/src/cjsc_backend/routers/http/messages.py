#!/usr/bin/env python3
from fastapi import APIRouter, Security, HTTPException
from fastapi_jwt import JwtAuthorizationCredentials
from loguru import logger
from psycopg2 import DatabaseError
from cjsc_backend import config
from cjsc_backend.database.tables import messages as db_msgs
from cjsc_backend.database.connect import create_connection_with_config
from cjsc_backend.routers.http.schemas.token import TokenSchema
# from cjsc_backend.routers.http.schemas.user import UserBaseSchema, \
#     UserLoginSchema, UserInfoSchema, UserSignupSchema

# See https://fastapi.tiangolo.com/tutorial/bigger-applications/

db = create_connection_with_config()

router = APIRouter(
    prefix="/msg",
    tags=['Messages', ],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}}
)


@router.post(
    "/chats",
)
async def messages_get_chats(
    credentials: JwtAuthorizationCredentials = Security(
        config.jwt_ac,
    ),
):
    logger.debug(
        f"Getting chats for user: {credentials["id"]}"
    )

    try:
        chats = db_msgs.get_user_chats(db, credentials["id"])
    except DatabaseError as e:
        logger.error(f"Failed to get user chats: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get user chats",
        )

    return {"chats": chats}
