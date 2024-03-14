#!/usr/bin/env python3
from pydantic import BaseModel
from datetime import datetime


# Pydantic models
class Message(BaseModel):  # Same as backend
    id: int | None = None
    from_user_id: int
    to_user_id: int
    is_read: bool = False
    content: str
    created_at: datetime = datetime.now()


class MessageRequestConfig(BaseModel):
    allow_faq: bool


class MessageRequest(BaseModel):
    message: Message
    config: MessageRequestConfig
