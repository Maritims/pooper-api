from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

from .animal_event_type_association import AnimalEventTypeAssociationRead
from .event import EventRead
from .event_type import EventType
from .note import NoteRead


class AnimalBase(BaseModel):
    name: str
    is_deactivated: Optional[bool]


class AnimalCreate(AnimalBase):
    event_types_to_track: List[EventType]


class AnimalRead(AnimalBase):
    id: int
    created: datetime
    updated: datetime
    events: List[EventRead]
    notes: List[NoteRead]
    tracked_event_types: List[AnimalEventTypeAssociationRead]

    class Config:
        orm_mode = True
