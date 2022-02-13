from typing import List

from pydantic import BaseModel

from src.models.event import EventRead


class TripBase(BaseModel):
    animal_id: int


class TripCreate(TripBase):
    event_ids: List[int]


class TripRead(TripBase):
    events: List[EventRead]
