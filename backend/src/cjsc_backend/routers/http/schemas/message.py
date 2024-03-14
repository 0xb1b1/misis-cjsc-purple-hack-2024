#!/usr/bin/env python3
from pydantic import BaseModel
from datetime import datetime


class Message(BaseModel):
    id: int | None = None
    from_user_id: int
    to_user_id: int
    is_read: bool = False
    content: str
    created_at: datetime = datetime.now()


# For ML-Queue
class MessageRequestConfig(BaseModel):
    allow_faq: bool


class MessageRequest(BaseModel):
    message: Message
    config: MessageRequestConfig
