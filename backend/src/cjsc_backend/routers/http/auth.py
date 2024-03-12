#!/usr/bin/env python3
from fastapi import APIRouter, Security, HTTPException
from fastapi_jwt import JwtAuthorizationCredentials
from loguru import logger
import bcrypt
from psycopg2 import DatabaseError
from cjsc_backend import config
from cjsc_backend.database.tables import users
from cjsc_backend.database.connect import create_connection_with_config
from cjsc_backend.routers.http.schemas.token import TokenSchema
from cjsc_backend.routers.http.schemas.user import UserBaseSchema, \
    UserLoginSchema, UserInfoSchema, UserSignupSchema

# See https://fastapi.tiangolo.com/tutorial/bigger-applications/

db = create_connection_with_config()

router = APIRouter(
    prefix="/auth",
    tags=['Authentication', ],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}}
)


@router.post(
    "/signup",
    response_model=TokenSchema,
)
async def signup(credentials: UserSignupSchema):
    logger.debug(
        f"A user tries to sign up (email: {credentials.email})")

    try:
        users.create(db, credentials)
    except DatabaseError as e:
        logger.info(
            f"User with email {credentials.email} already exists \
or other error: {e}"
        )
        raise HTTPException(
            status_code=400,
            detail="User already exists",
        )

    try:
        user = users.get(db, email=credentials.email)
    except DatabaseError as e:
        logger.info(
            f"User with email {credentials.email} does not exist \
or other error: {e}"
        )
    logger.debug(f"Got user from DB: {user}")

    subject = {
        "id": user.id if user.role != "operator" else 0,
        "email": user.email,
        "role": user.role,
    }

    return {
        "access_token": config.jwt_ac.create_access_token(
            subject=subject
        )
    }


@router.post(
    "/login",
    response_model=TokenSchema,
)
async def login(credentials: UserLoginSchema):
    logger.debug(
        f"A user tries to sign in (email: {credentials.email})..."
    )

    try:
        user = users.get(db, email=credentials.email)
    except DatabaseError as e:
        logger.info(
            f"User with email {credentials.email} does not exist \
or other error: {e}"
        )
    logger.debug(f"Got user from DB: {user}")
    logger.critical(f"User password hash: {str(user.password_hash.encode('utf-8').decode())}")

    # Check BCrypt hash
    is_password_correct = bcrypt.checkpw(
        credentials.password.encode("utf-8"),
        user.password_hash.encode("utf-8"),
    )

    if not is_password_correct:
        raise HTTPException(
            status_code=400,
            detail="Invalid credentials",
        )

    subject = {
        "id": user.id if user.role != "operator" else 0,
        "email": user.email,
        "role": user.role,
    }
    return {
        "access_token": config.jwt_ac.create_access_token(
            subject=subject
        )
    }


@router.get(
    "/me/token",
    response_model=UserInfoSchema,
)
def auth_token_info(
    credentials: JwtAuthorizationCredentials = Security(
        config.jwt_ac,
    ),
):
    return UserInfoSchema(
        id=credentials["id"],
        email=credentials["email"],
        role=credentials["role"],
    )


@router.get(
    "/me/full",
    response_model=UserBaseSchema,
)
def auth_full_info(
    credentials: JwtAuthorizationCredentials = Security(
        config.jwt_ac,
    ),
):
    return users.get(db, email=credentials["email"])
