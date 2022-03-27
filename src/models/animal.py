from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

from .animal_condition_type_association import AnimalConditionTypeAssociationRead
from .animal_event_type_association import AnimalEventTypeAssociationRead
from .animal_weight import AnimalWeightRead
from .condition import ConditionRead
from .condition_type import ConditionType
from .event import EventRead
from .event_type import EventType
from .note import NoteRead


class AnimalBase(BaseModel):
    name: str
    is_deactivated: Optional[bool]


class AnimalCreate(AnimalBase):
    condition_types_to_track: List[ConditionType]
    event_types_to_track: List[EventType]


class AnimalRead(AnimalBase):
    id: int
    created: datetime
    updated: datetime
    tracked_conditions: List[ConditionRead]
    tracked_events: List[EventRead]
    notes: List[NoteRead]
    tracked_condition_types: List[AnimalConditionTypeAssociationRead]
    tracked_event_types: List[AnimalEventTypeAssociationRead]
    weight_history: List[AnimalWeightRead]

    class Config:
        orm_mode = True
