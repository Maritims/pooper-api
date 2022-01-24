import datetime
from typing import List
from fastapi import APIRouter, status, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import func
from sqlmodel import Session

from ..auth import oauth2_scheme
from ..database import get_database_session, Animal
from ..models.animal import AnimalRead

router = APIRouter(
    prefix="/animals",
    tags=["animals"],
    dependencies=[Depends(oauth2_scheme)]
)


class AnimalCreate(BaseModel):
    name: str


@router.get("/count", response_model=int)
def get_count(session: Session = Depends(get_database_session)):
    return session.query(func.count(Animal.id)).scalar()


@router.get("/", response_model=List[AnimalRead])
def get_all(page: int = 0, page_size: int = 100, session: Session = Depends(get_database_session)):
    return session.query(Animal).offset(page).limit(page_size).all()


@router.get("/{_id}", response_model=AnimalRead)
def get_by_id(_id, session: Session = Depends(get_database_session)):
    animal = session.query(Animal).where(Animal.id == _id).first()

    if animal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"animal with id {_id} was not found"
        )

    return animal


@router.post("/", response_model=AnimalRead, status_code=status.HTTP_201_CREATED)
def create(animal: AnimalCreate, session: Session = Depends(get_database_session)):
    db_animal = Animal(**animal.dict())
    db_animal.created = datetime.datetime.now()
    db_animal.updated = datetime.datetime.now()

    session.add(db_animal)
    session.commit()
    session.refresh(db_animal)

    return db_animal


@router.put("/{_id}", response_model=AnimalRead)
def update(_id: int, animal: AnimalCreate, session: Session = Depends(get_database_session)):
    db_animal = session.query(Animal).where(Animal.id == _id).first()

    if db_animal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"animal with id {_id} was not found"
        )

    db_animal.name = animal.name
    db_animal.updated = datetime.datetime.now()

    session.add(db_animal)
    session.commit()
    session.refresh(db_animal)

    return db_animal


@router.delete("/{_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(_id, session: Session = Depends(get_database_session)):
    animal = session.query(Animal).where(Animal.id == _id).first()

    if animal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"animal with id {_id} was not found"
        )

    session.delete(animal)
    session.commit()
