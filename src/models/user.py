from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class UserBase(BaseModel):
    first_name: str
    last_name: str
    email_address: str
    home_longitude: Optional[float]
    home_latitude: Optional[float]


class UserCreate(UserBase):
    password: str
    password_repeated: str


class UserRead(UserBase):
    id: int
    is_disabled: bool
    created: datetime
    updated: datetime

    class Config:
        orm_mode = True
