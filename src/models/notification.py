from pydantic import BaseModel


class NotificationBase(BaseModel):
    title: str
    message: str


class NotificationRead()