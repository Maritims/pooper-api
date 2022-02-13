from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from ..auth import pwd_context, oauth2_scheme
from ..database import get_database_session, User
from ..models.user import UserRead, UserCreate
from ..services.users import get_current_user

router = APIRouter(
    prefix="/users",
    tags=["users"]
)


@router.get("/me", response_model=UserRead)
def get_me(session: Session = Depends(get_database_session), token: str = Depends(oauth2_scheme)):
    return get_current_user(session, token)


@router.get("/", response_model=List[UserRead])
def get_all_users(page: int = 0, page_size: int = 100, session: Session = Depends(get_database_session)):
    return session.query(User).offset(page).limit(page_size).all()


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create(user: UserCreate, session: Session = Depends(get_database_session)):
    if user.password != user.password_repeated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Passwords must match"
        )

    db_user = User(
        first_name=user.first_name,
        last_name=user.last_name,
        email_address=user.email_address,
        password_hash=pwd_context.hash(user.password),
        is_disabled=False,
        created=datetime.now(),
        updated=datetime.now()
    )

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


@router.patch("/update", response_model=UserRead)
def update(user: UserCreate, session: Session = Depends(get_database_session), token: str = Depends(oauth2_scheme)):
    if user.password != user.password_repeated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Passwords must match"
        )

    db_user: User = get_current_user(session, token)
    db_user.email_address = user.email_address
    db_user.first_name = user.first_name
    db_user.last_name = user.last_name
    db_user.home_longitude = user.home_longitude
    db_user.home_latitude = user.home_latitude
    db_user.updated = datetime.now()

    if user.password is not None:
        db_user.password_hash = pwd_context.hash(user.password)

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


@router.delete("/{_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(_id, session: Session = Depends(get_database_session)):
    user = session.query(User).where(User.id == _id).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"user with id {_id} was not found"
        )

    session.delete(user)
    session.commit()
