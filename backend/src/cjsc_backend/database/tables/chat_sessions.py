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


# def _check