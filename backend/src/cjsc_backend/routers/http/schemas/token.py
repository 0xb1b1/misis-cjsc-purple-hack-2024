#!/usr/bin/env python3
from pydantic import BaseModel


class TokenSchema(BaseModel):
    access_token: str
