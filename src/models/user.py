from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from src.models.color_theme import ColorTheme


class UserBase(BaseModel):
    first_name: str
    last_name: str
    email_address: str
    home_longitude: Optional[float]
    home_latitude: Optional[float]
    color_theme: Optional[ColorTheme]


class UserCreate(UserBase):
    password: str
    password_repeated: str


class UserRead(UserBase):
    id: int
    is_disabled: bool
    created: datetime
    updated: datetime
    color_theme: Optional[ColorTheme]

    class Config:
        orm_mode = True
