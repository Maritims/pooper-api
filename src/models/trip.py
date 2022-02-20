from typing import List

from pydantic import BaseModel


class TripBase(BaseModel):
    pass


class TripCreate(TripBase):
    event_ids: List[int]


class TripRead(TripBase):
    id: int
    created_by_user_id: int

    class Config:
        orm_mode = True
