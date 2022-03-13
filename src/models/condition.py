from datetime import datetime

from pydantic import BaseModel

from src.models.condition_type import ConditionType


class ConditionBase(BaseModel):
    animal_id: int
    condition_type: ConditionType
    is_enabled: bool


class ConditionCreate(ConditionBase):
    pass


class ConditionRead(ConditionBase):
    id: int
    created: datetime
    updated: datetime

    class Config:
        orm_mode = True
