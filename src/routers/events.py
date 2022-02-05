from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy import func, text
from sqlalchemy.orm import Session, Query

from ..auth import oauth2_scheme
from ..database import get_database_session, Event
from ..models.event import EventRead, EventCreate
from ..models.event_type import EventType

router = APIRouter(
    prefix="/events",
    tags=["events"],
    dependencies=[Depends(oauth2_scheme)]
)


def get_statement(
        session: Session,
        animal_id: Optional[int] = None,
        event_type: Optional[EventType] = None,
        days: Optional[int] = None) -> Query:
    statement: Query = session.query(Event)

    if animal_id is not None and animal_id > 0:
        statement = statement.where(Event.animal_id == animal_id)

    if EventType.has_value(event_type):
        statement = statement.where(Event.event_type == event_type)

    if days is not None:
        statement = statement.where(func.datediff(datetime.now(), Event.created) <= days)

    return statement


@router.get("/count", response_model=int)
def get_count(
        animal_id: Optional[int] = None,
        event_type: Optional[EventType] = None,
        days: Optional[int] = None,
        session: Session = Depends(get_database_session)):
    return get_statement(session, animal_id, event_type, days).count()


@router.get("/{_id}", response_model=EventRead)
def get_event(_id: int, session: Session = Depends(get_database_session)):
    event = session.query(Event).where(Event.id == _id).first()

    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"event with id {_id} was not found")

    return event


@router.get("/", response_model=List[EventRead])
def get_all(
        animal_id: Optional[int] = None,
        event_type: Optional[EventType] = None,
        days: Optional[int] = None,
        page: int = 0,
        page_size: int = 100,
        sort_order: str = "desc",
        session: Session = Depends(get_database_session)):
    statement: Query = get_statement(session, animal_id, event_type, days)

    if sort_order == "asc":
        statement = statement.order_by(Event.id.asc())
    else:
        statement = statement.order_by(Event.id.desc())

    return statement.limit(page_size).offset(page * page_size).all()


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
