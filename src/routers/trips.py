from datetime import datetime
from typing import List

from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session

from src.auth import oauth2_scheme
from src.database import get_database_session, Trip, Event
from src.models.trip import TripRead, TripCreate
from src.services.users import get_current_user

router = APIRouter(
    prefix="/trips",
    tags=["trips"],
    dependencies=[Depends(oauth2_scheme)]
)


@router.get("/", response_model=List[TripRead])
def get_all(session: Session = Depends(get_database_session)):
    trips = session.query(Trip).all()
    return trips


@router.post("/", response_model=TripRead)
def create(trip: TripCreate, session: Session = Depends(get_database_session), token: str = Depends(oauth2_scheme)):
    current_user = get_current_user(session, token)

    db_trip = Trip(
        created_by_user_id=current_user.id,
        created_date=datetime.now(),
        animal_id=trip.animal_id
    )

    session.add(db_trip)
    session.commit()

    for event_id in trip.event_ids:
        db_event = session.query(Event.id == event_id)
        db_event.trip_id = db_trip.id
        session.add(db_event)

    session.commit()
    session.refresh(db_trip)

    return db_trip
