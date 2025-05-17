# app/schemas/push_token.py

from pydantic import BaseModel

class PushTokenCreate(BaseModel):
    fcm_token: str


class TokenOut(PushTokenCreate):
    token_id : int