from datetime import datetime

from pydantic import BaseModel

from src.models.event_type import EventType


class AnimalEventTypeAssociationBase(BaseModel):
    animal_id: int
    event_type: EventType


class AnimalEventTypeAssociationWrite(AnimalEventTypeAssociationBase):
    pass


class AnimalEventTypeAssociationRead(AnimalEventTypeAssociationBase):
    created: datetime
    created_by_user_id: int
    updated: datetime
    updated_by_user_id: int

    class Config:
        orm_mode = True
