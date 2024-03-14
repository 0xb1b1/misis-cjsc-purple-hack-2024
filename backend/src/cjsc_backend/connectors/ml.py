#!/usr/bin/env python3
import requests
from loguru import logger
from cjsc_backend.routers.http.schemas.message import \
    Message, MessageRequest, MessageRequestConfig
from cjsc_backend import config


def query(message: Message) -> None:
    stripped_message = Message(  # Needed to avoid serialization issues
        from_user_id=message.from_user_id,
        to_user_id=message.to_user_id,
        content=message.content,
    )
    mrc = MessageRequestConfig(
        allow_faq=True,  # TODO: check this value with the ML team
    )

    mr = MessageRequest(
        message=stripped_message,
        config=mrc,
    )

    r = requests.post(
        f"{config.ML_URL}/query_ml",
        json=mr.model_dump(exclude_unset=True),
        params={"ca_secret": config.CROSS_APP_SECRET},
    )

    logger.debug(f"Sent message to ML Query: {r.status_code=} {r.json()=}")

