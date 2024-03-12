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
    UserLoginSchema, UserInfoSchema

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
async def signup(credentials: UserBaseSchema):
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

    subject = {
        "email": credentials.email,
        "role": credentials.role,
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
        f"A user tries to sign in (email: {credentials.email})"
    )
    # user = repo.find_one_by({"email": credentials.email})
    # if user is None:
    #     raise HTTPException(
    #         status_code=400,
    #         detail="Invalid credentials",
    #     )

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
        "email": user.email,
        "role": user.role,
    }
    return {
        "access_token": config.jwt_ac.create_access_token(
            subject=subject
        )
    }


@router.get(
    "/me",
    response_model=UserInfoSchema,
)
def user(
    credentials: JwtAuthorizationCredentials = Security(
        config.jwt_ac,
    ),
):
    return UserInfoSchema(
        email=credentials["email"],
        role=credentials["role"],
    )
