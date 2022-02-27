from datetime import datetime

from pydantic import BaseModel


class NoteBase(BaseModel):
    animal_id: int
    text: str


class NoteCreate(NoteBase):
    pass


class NoteRead(NoteBase):
    id: int
    created: datetime
    created_by_user_name: str
    updated: datetime
    updated_by_user_name: str

    class Config:
        orm_mode = True
