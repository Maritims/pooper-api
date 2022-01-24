from datetime import datetime
from pydantic import BaseModel
from .event_type import EventType


class EventBase(BaseModel):
    latitude: float
    longitude: float
    animal_id: int
    event_type: EventType


class EventCreate(EventBase):
    pass


class EventRead(EventBase):
    id: int
    created: datetime
    animal_name: str

    class Config:
        orm_mode = True
