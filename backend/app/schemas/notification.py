from pydantic import BaseModel, EmailStr, Field
from typing import List


class NotificationSubscribe(BaseModel):
    email: EmailStr
    pisos: List[int] = Field(..., min_items=1, max_items=3)
    niveles: List[str] = Field(..., min_items=1)


class NotificationSubscribeResponse(BaseModel):
    message: str
    email: EmailStr
    subscribed: bool

