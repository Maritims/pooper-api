from datetime import datetime
from typing import List, Optional

import fastapi
from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy import func, or_
from sqlalchemy.orm import Session, Query

from ..auth import oauth2_scheme
from ..database import get_database_session, Event, Animal
from ..models.event import EventRead, EventCreate
from ..models.event_type import EventType
from ..services.notifications import send_notification_to_users
from ..services.users import get_current_user

router = APIRouter(
    prefix="/events",
    tags=["events"],
    dependencies=[Depends(oauth2_scheme)]
)


def get_statement(
        session: Session,
        animal_ids: Optional[List[int]] = None,
        event_type: Optional[EventType] = None,
        days: Optional[int] = None,
        has_trip: Optional[bool] = None) -> Query:
    statement: Query = session.query(Event).filter(Event.animal.has(Animal.is_deactivated.is_not(True)))

    if animal_ids is not None and len(animal_ids) > 0:
        statement = statement.where(Event.animal_id.in_(animal_ids))

    if EventType.has_value(event_type):
        statement = statement.where(Event.event_type == event_type)

    if days is not None:
        if days == 1:
            statement = statement.where(func.date(Event.created) == func.date(datetime.now()))
        else:
            statement = statement.where(func.datediff(datetime.now(), Event.created) <= days)

    if has_trip is True:
        statement = statement.filter(or_(Event.trip_id.is_not(None), Event.trip_id > 0))
    elif has_trip is False:
        statement = statement.filter(or_(Event.trip_id.is_(None), Event.trip_id == 0))

    return statement


@router.get("/count", response_model=int)
def get_count(
        animal_ids: Optional[List[int]] = fastapi.Query(None),
        event_type: Optional[EventType] = None,
        days: Optional[int] = None,
        has_trip: Optional[bool] = None,
        session: Session = Depends(get_database_session)):
    return get_statement(session, animal_ids, event_type, days, has_trip).count()


@router.get("/{_id}", response_model=EventRead)
def get_event(_id: int, session: Session = Depends(get_database_session)):
    event = session.query(Event).where(Event.id == _id).first()

    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"event with id {_id} was not found")

    return event


@router.get("/", response_model=List[EventRead])
def get_all(
        animal_ids: Optional[List[int]] = fastapi.Query(None),
        event_type: Optional[EventType] = None,
        days: Optional[int] = None,
        has_trip: Optional[bool] = None,
        page: int = 0,
        page_size: int = 100,
        sort_order: str = "desc",
        session: Session = Depends(get_database_session)):
    statement: Query = get_statement(session, animal_ids, event_type, days, has_trip)

    if sort_order == "asc":
        statement = statement.order_by(Event.id.asc())
    else:
        statement = statement.order_by(Event.id.desc())

    return statement.limit(page_size).offset(page * page_size).all()


@router.post("/", response_model=EventRead, status_code=status.HTTP_201_CREATED)
def create(event: EventCreate, session: Session = Depends(get_database_session), token: str = Depends(oauth2_scheme)):
    current_user = get_current_user(session, token)

    db_event = Event(**event.dict())
    if db_event.created is None:
        db_event.created = datetime.now()
    db_event.created_by_user_id = current_user.id
    db_event.updated = datetime.now()
    db_event.updated_by_user_id = current_user.id

    session.add(db_event)
    session.commit()
    session.refresh(db_event)

    send_notification_to_users(f"{current_user.first_name} registered a new event",
                               f"{db_event.event_type} was registered for {db_event.animal_name}.",
                               [current_user.id],
                               session,
                               token)

    return db_event


@router.delete("/{_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(_id, session: Session = Depends(get_database_session)):
    event = session.query(Event).where(Event.id == _id).first()

    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"event with id {id} was not found")

    session.delete(event)
    session.commit()
