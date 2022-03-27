from datetime import datetime

from pydantic import BaseModel


class AnimalWeightBase(BaseModel):
    animal_id: int
    weight_in_grams: float


class AnimalWeightCreate(AnimalWeightBase):
    pass


class AnimalWeightRead(AnimalWeightBase):
    id: int
    created: datetime

    class Config:
        orm_mode = True
