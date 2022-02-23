import datetime
from typing import List, Optional

from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy import func
from sqlalchemy.orm import Query
from sqlmodel import Session

from ..auth import oauth2_scheme
from ..database import get_database_session, Animal
from ..models.animal import AnimalRead, AnimalCreate
from ..services.users import get_current_user

router = APIRouter(
    prefix="/animals",
    tags=["animals"],
    dependencies=[Depends(oauth2_scheme)]
)


@router.get("/count", response_model=int)
def get_count(session: Session = Depends(get_database_session)):
    return session.query(func.count(Animal.id)).scalar()


@router.get("/", response_model=List[AnimalRead])
def get_all(
        include_deactivated: bool = False,
        page: int = 0,
        page_size: int = 100,
        session: Session = Depends(get_database_session)
):
    statement: Query = session.query(Animal)

    if include_deactivated is False:
        statement = statement.where(Animal.is_deactivated.is_not(True))

    return statement.offset(page).limit(page_size).all()


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
def create(animal: AnimalCreate, session: Session = Depends(get_database_session), token: str = Depends(oauth2_scheme)):
    user = get_current_user(session, token)
    db_animal = Animal(**animal.dict())
    db_animal.created = datetime.datetime.now()
    db_animal.created_by_user_id = user.id
    db_animal.updated = datetime.datetime.now()
    db_animal.updated_by_user_id = user.id

    session.add(db_animal)
    session.commit()
    session.refresh(db_animal)

    return db_animal


@router.put("/{_id}", response_model=AnimalRead)
def update(
        _id: int,
        animal: AnimalCreate,
        session: Session = Depends(get_database_session),
        token: str = Depends(oauth2_scheme)
):
    user = get_current_user(session, token)
    db_animal = session.query(Animal).where(Animal.id == _id).first()

    if db_animal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"animal with id {_id} was not found"
        )

    db_animal.name = animal.name
    db_animal.is_deactivated = animal.is_deactivated
    db_animal.updated = datetime.datetime.now()
    db_animal.updated_by_user_id = user.id

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
