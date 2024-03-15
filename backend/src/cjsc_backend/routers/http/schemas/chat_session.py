#!/usr/bin/env python3
from pydantic import BaseModel
from datetime import datetime


class ChatSession(BaseModel):
    id: int | None = None
    user_1_id: int
    user_2_id: int
    allow_ml: bool = True
    allow_faq: bool = True
    created_at: datetime | None = None
