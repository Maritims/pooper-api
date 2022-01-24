from datetime import datetime
from typing import List

from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..auth import oauth2_scheme
from ..database import get_database_session, Event
from ..models.event import EventRead, EventCreate

router = APIRouter(
    prefix="/events",
    tags=["events"],
    dependencies=[Depends(oauth2_scheme)]
)


@router.get("/count", response_model=int)
def get_count(session: Session = Depends(get_database_session)):
    return session.query(func.count(Event.id)).scalar()


@router.get("/{_id}", response_model=EventRead)
def get_event(_id: int, session: Session = Depends(get_database_session)):
    event = session.query(Event).where(Event.id == _id).first()

    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"event with id {_id} was not found")

    return event


@router.get("/", response_model=List[EventRead])
def get_all(page: int = 0, page_size: int = 100, session: Session = Depends(get_database_session)):
    return session.query(Event).offset(page).limit(page_size).all()


@router.post("/", response_model=EventRead, status_code=status.HTTP_201_CREATED)
def create(event: EventCreate, session: Session = Depends(get_database_session)):
    db_event = Event(**event.dict())
    db_event.created = datetime.now()
    db_event.updated = datetime.now()

    session.add(db_event)
    session.commit()
    session.refresh(db_event)

    return db_event


@router.delete("/{_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(_id, session: Session = Depends(get_database_session)):
    event = session.query(Event).where(Event.id == _id).first()

    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"event with id {id} was not found")

    session.delete(event)
    session.commit()
