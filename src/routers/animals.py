from datetime import datetime
import logging
from typing import List, Optional

from fastapi import APIRouter, status, HTTPException, Depends
import fastapi
from sqlalchemy import func
from sqlalchemy.orm import Query, noload
from sqlmodel import Session

from ..auth import oauth2_scheme
from ..database import get_database_session, Animal, Note, AnimalEventTypeAssociation, AnimalConditionTypeAssociation, \
    Condition, AnimalWeight
from ..models.animal import AnimalRead, AnimalCreate
from ..models.animal_weight import AnimalWeightRead, AnimalWeightCreate
from ..models.condition_type import ConditionType
from ..models.event_type import EventType
from ..models.note import NoteCreate, NoteRead
from ..services.users import get_current_user

router = APIRouter(
    prefix="/animals",
    tags=["animals"],
    dependencies=[Depends(oauth2_scheme)]
)

log = logging.getLogger(__name__)


@router.get("/count", response_model=int)
def get_animal_count(session: Session = Depends(get_database_session)):
    return session.query(func.count(Animal.id)).scalar()


@router.get("/", response_model=List[AnimalRead])
def get_all_animals(
        include_deactivated: bool = False,
        include_events: bool = False,
        include_conditions: bool = False,
        include_weight_history: bool = False,
        page: int = 0,
        page_size: int = 100,
        session: Session = Depends(get_database_session)
):
    statement: Query = session.query(Animal)

    statement = statement if include_deactivated is True else statement.where(Animal.is_deactivated.is_not(True))
    statement = statement if include_events is True else statement.options(noload('tracked_events'))
    statement = statement if include_conditions is True else statement.options(noload('tracked_conditions'))
    statement = statement.join(AnimalWeight) if include_weight_history is True else statement

    return statement.offset(page).limit(page_size).all()


@router.get("/weight", response_model=List[AnimalWeightRead])
def get_animal_weight_history(
        animal_ids: Optional[List[int]] = fastapi.Query(None),
        days: Optional[int] = None,
        session: Session = Depends(get_database_session)
):
    statement: Query = session.query(AnimalWeight)

    if animal_ids is not None and len(animal_ids) > 0:
        statement = statement.where(AnimalWeight.animal_id.in_(animal_ids))

    if days is not None:
        if days == 1:
            statement = statement.where(func.date(AnimalWeight.created) == func.date(datetime.now()))
        else:
            statement = statement.where(func.datediff(datetime.now(), AnimalWeight.created) <= days)

    db_animal_weight_history = statement\
        .order_by(AnimalWeight.id.desc())\
        .all()

    return db_animal_weight_history


@router.get("/{_id}", response_model=AnimalRead)
def get_animal_by_id(_id, session: Session = Depends(get_database_session)):
    animal = session.query(Animal).where(Animal.id == _id).first()

    if animal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"animal with id {_id} was not found"
        )

    return animal


@router.post("/", response_model=AnimalRead, status_code=status.HTTP_201_CREATED)
def create_animal(animal: AnimalCreate, session: Session = Depends(get_database_session), token: str = Depends(oauth2_scheme)):
    user = get_current_user(session, token)

    db_animal = Animal()
    db_animal.name = animal.name
    db_animal.is_deactivated = animal.is_deactivated
    db_animal.created = datetime.now()
    db_animal.created_by_user_id = user.id
    db_animal.updated = datetime.now()
    db_animal.updated_by_user_id = user.id

    for tracked_condition_type in animal.condition_types_to_track:
        db_association = AnimalConditionTypeAssociation()
        db_association.created = datetime.now()
        db_association.created_by_user_id = user.id
        db_association.updated = datetime.now()
        db_association.updated_by_user_id = user.id
        db_association.condition_type = tracked_condition_type
        db_animal.tracked_condition_types.append(db_association)

    for tracked_event_type in animal.event_types_to_track:
        db_association = AnimalEventTypeAssociation()
        db_association.created = datetime.now()
        db_association.created_by_user_id = user.id
        db_association.updated = datetime.now()
        db_association.updated_by_user_id = user.id
        db_association.event_type = tracked_event_type
        db_animal.tracked_event_types.append(db_association)

    session.add(db_animal)
    session.commit()
    session.refresh(db_animal)

    return db_animal


@router.put("/{_id}", response_model=AnimalRead)
def update_animal(
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
    if animal.is_deactivated is None:
        db_animal.is_deactivated = False
    else:
        db_animal.is_deactivated = animal.is_deactivated
    db_animal.updated = datetime.now()
    db_animal.updated_by_user_id = user.id

    # Removed all tracked condition types
    session.query(AnimalConditionTypeAssociation).where(AnimalConditionTypeAssociation.animal_id == _id).delete()

    # Add condition types to track
    for condition_type in animal.condition_types_to_track:
        is_untracked = True
        for tracked_condition_type in db_animal.tracked_condition_types:
            if ConditionType(tracked_condition_type.condition_type) == condition_type:
                is_untracked = False

        if is_untracked is True:
            db_animal.tracked_condition_types.append(AnimalConditionTypeAssociation(
                condition_type=condition_type,
                created=datetime.now(),
                created_by_user_id=user.id,
                updated=datetime.now(),
                updated_by_user_id=user.id
            ))

    # Removed all tracked event types
    session.query(AnimalEventTypeAssociation).where(AnimalEventTypeAssociation.animal_id == _id).delete()

    # Add event types to track
    for event_type in animal.event_types_to_track:
        is_untracked = True
        for tracked_event_type in db_animal.tracked_event_types:
            if EventType(tracked_event_type.event_type) == event_type:
                is_untracked = False

        if is_untracked is True:
            db_animal.tracked_event_types.append(AnimalEventTypeAssociation(
                event_type=event_type,
                created=datetime.now(),
                created_by_user_id=user.id,
                updated=datetime.now(),
                updated_by_user_id=user.id
            ))

    session.commit()
    session.refresh(db_animal)

    return db_animal


@router.delete("/{_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_animal(_id: int, session: Session = Depends(get_database_session)):
    animal = session.query(Animal).where(Animal.id == _id).first()

    if animal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"animal with id {_id} was not found"
        )

    session.delete(animal)
    session.commit()


@router.get("/note", response_model=List[NoteRead])
def get_all_notes(session: Session = Depends(get_database_session)):
    notes = session.query(Note).all()
    return notes


@router.post("/note", response_model=NoteRead, status_code=status.HTTP_201_CREATED)
def create_note(note: NoteCreate, session: Session = Depends(get_database_session), token: str = Depends(oauth2_scheme)):
    user = get_current_user(session, token)

    db_note = Note(**note.dict())
    db_note.created = datetime.now()
    db_note.created_by_user_id = user.id
    db_note.updated = datetime.now()
    db_note.updated_by_user_id = user.id

    session.add(db_note)
    session.commit()
    session.refresh(db_note)

    return db_note


@router.put("/note/{_id}", response_model=NoteRead)
def update_note(
        _id: int,
        note: NoteCreate,
        session: Session = Depends(get_database_session),
        token: str = Depends(oauth2_scheme)
):
    user = get_current_user(session, token)
    db_note = session.query(Note).where(Note.id == _id).first()

    if db_note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"note with id {_id} was not found"
        )

    db_note.text = note.text
    db_note.updated = datetime.now()
    db_note.updated_by_user_id = user.id

    session.add(db_note)
    session.commit()
    session.refresh(db_note)

    return db_note


@router.delete("/note/{_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(_id, session: Session = Depends(get_database_session)):
    note = session.query(Note).where(Note.id == _id).first()

    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"note with id {_id} was not found"
        )

    session.delete(note)
    session.commit()


@router.put("/{_id}/{condition_type}", response_model=AnimalRead)
def toggle_condition(
        _id: int,
        condition_type: ConditionType,
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

    done = False
    for tracked_condition in db_animal.tracked_conditions:
        if ConditionType(tracked_condition.condition_type) == condition_type:
            tracked_condition.is_enabled = not tracked_condition.is_enabled
            tracked_condition.updated = datetime.now()
            tracked_condition.updated_by_user_id = user.id
            done = True

    if not done:
        db_animal.tracked_conditions.append(Condition(
            animal_id=_id,
            condition_type=condition_type,
            is_enabled=True,
            created=datetime.now(),
            created_by_user_id=user.id,
            updated=datetime.now(),
            updated_by_user_id=user.id
        ))

    session.commit()
    return db_animal


@router.get("/{_id}/weight", response_model=AnimalWeightRead)
def get_current_animal_weight(_id: int, session: Session = Depends(get_database_session)):
    db_current_animal_weight = session.query(AnimalWeight)\
        .where(AnimalWeight.animal_id == _id)\
        .order_by(AnimalWeight.id.desc())\
        .first()

    return db_current_animal_weight


@router.post("/weight", response_model=AnimalWeightRead, status_code=status.HTTP_201_CREATED)
def create_animal_weight(
        weight: AnimalWeightCreate,
        session: Session = Depends(get_database_session),
        token: str = Depends(oauth2_scheme)
):
    user = get_current_user(session, token)

    db_animal_weight = AnimalWeight()
    db_animal_weight.animal_id = weight.animal_id
    db_animal_weight.weight_in_grams = weight.weight_in_grams
    db_animal_weight.created_by_user_id = user.id
    db_animal_weight.created = datetime.now()
    db_animal_weight.updated_by_user_id = user.id
    db_animal_weight.updated = datetime.now()

    session.add(db_animal_weight)
    session.commit()
    session.refresh(db_animal_weight)

    return db_animal_weight


@router.delete("/weight/{_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_animal_weight(_id: int, session: Session = Depends(get_database_session)):
    db_animal_weight = session.query(AnimalWeight).where(AnimalWeight.id == _id).first()

    if db_animal_weight is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"weight with id {_id} was not found"
        )

    session.delete(db_animal_weight)
    session.commit()
