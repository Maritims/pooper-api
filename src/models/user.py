from datetime import datetime
from pydantic import BaseModel


class UserBase(BaseModel):
    first_name: str
    last_name: str
    email_address: str
    home_longitude: float
    home_latitude: float


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
