from datetime import datetime

from pydantic import BaseModel


class NotificationBase(BaseModel):
    title: str
    message: str


class NotificationCreate(NotificationBase):
    pass


class NotificationRead(NotificationBase):
    int: int
    created: datetime
    created_by_user_name: str

    class Config:
        orm_mode = True

