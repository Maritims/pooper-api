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


class EventCreate(EventBase):
    pass


class EventRead(EventBase):
    id: int
    created: datetime
    animal_name: str

    class Config:
        orm_mode = True
