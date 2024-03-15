#!/usr/bin/env python3
from datetime import datetime

import requests
from pydantic import BaseModel


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


mr = MessageRequest(
    message=Message(
        from_user_id=1, to_user_id=0, content="Hello, this is a test message."
    ),
    config=MessageRequestConfig(allow_faq=True),
)

mr_json = mr.model_dump(exclude_unset=True)
r = requests.post("http://localhost:8081/query_ml", json=mr_json)
