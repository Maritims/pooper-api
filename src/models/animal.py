from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from .event import EventRead


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

    class Config:
        orm_mode = True
