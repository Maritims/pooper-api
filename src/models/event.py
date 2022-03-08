from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from .event_type import EventType


class EventBase(BaseModel):
    latitude: float
    longitude: float
    animal_id: int
    event_type: EventType
    rating: Optional[int]
    created: datetime


class EventCreate(EventBase):
    created: Optional[datetime]


class EventRead(EventBase):
    id: int
    created_by_user_id: int
    created_by_user_name: str
    animal_name: str
    trip_id: Optional[int]
    is_tracked: bool

    class Config:
        orm_mode = True
