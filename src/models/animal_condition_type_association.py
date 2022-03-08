from datetime import datetime

from pydantic import BaseModel

from src.models.condition_type import ConditionType


class AnimalConditionTypeAssociationBase(BaseModel):
    animal_id: int
    condition_type: ConditionType


class AnimalConditionTypeAssociationWrite(AnimalConditionTypeAssociationBase):
    pass


class AnimalConditionTypeAssociationRead(AnimalConditionTypeAssociationBase):
    created: datetime
    created_by_user_id: int
    updated: datetime
    updated_by_user_id: int

    class Config:
        orm_mode = True
