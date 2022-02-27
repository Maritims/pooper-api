from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from .event import EventRead
from .note import NoteRead


class AnimalBase(BaseModel):
    name: str
    is_deactivated: Optional[bool]


class AnimalCreate(AnimalBase):
    pass


class AnimalRead(AnimalBase):
    id: int
    created: datetime
    updated: datetime
    events: List[EventRead]
    notes: List[NoteRead]

    class Config:
        orm_mode = True
