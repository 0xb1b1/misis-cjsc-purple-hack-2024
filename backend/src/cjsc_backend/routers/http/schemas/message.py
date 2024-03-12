#!/usr/bin/env python3
from pydantic import BaseModel
from datetime import datetime


class Message(BaseModel):
    id: int
    from_user_id: int
    to_user_id: int
    is_read: bool
    content: str
    created_at: datetime = datetime.now()
