#!/usr/bin/env python3
from psycopg2 import DatabaseError
from fastapi import APIRouter, Security, HTTPException
from fastapi_jwt import JwtAuthorizationCredentials
from loguru import logger
from cjsc_backend import config
from cjsc_backend.database.connect import create_connection_with_config
from cjsc_backend.routers.http.schemas.token import TokenSchema
from cjsc_backend.routers.http.schemas.user import UserBaseSchema, \
    UserLoginSchema, UserInfoSchema

# See https://fastapi.tiangolo.com/tutorial/bigger-applications/

db = create_connection_with_config()

router = APIRouter(
    prefix="/debug",
    tags=['Debug', ],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}}
)


@router.get("/users/all")
async def debug_users_all():
    logger.debug("Listing all users...")
    with db.cursor() as curs:
        try:
            curs.execute("SELECT * FROM users")
            return curs.fetchall()
        except DatabaseError as e:
            logger.error(f"Failed to get all users: {e}")
            return None
