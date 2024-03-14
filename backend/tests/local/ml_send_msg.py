#!/usr/bin/env python3
from os import getenv
import random
import requests
from pydantic import BaseModel
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


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


print(f"{getenv("CJSC_CROSS_APP_SECRET")=}")


print("Sending message without shared secret")  # THIS WILL GIVE AN ERROR
message = Message(
    from_user_id=1,
    to_user_id=2,
    content="Hello"
)
r = requests.post(
    "http://127.0.0.1:8080/msg/send",
    json=message.model_dump(exclude_unset=True),
)
print(f"{r.status_code=} {r.json()=}")

print("Sending message with shared secret")  # THIS WILL WORK!
message = Message(
    from_user_id=0,
    to_user_id=1,
    content=f"Hello #{random.randint(0, 100)}"
)
# send ca_secret query parameter (?ca_secret=...)
r = requests.post(
    "http://127.0.0.1:8080/msg/send",
    json=message.model_dump(exclude_unset=True),
    params={"ca_secret": getenv("CJSC_CROSS_APP_SECRET")}
)
print(f"{r.status_code=} {r.json()=}")
