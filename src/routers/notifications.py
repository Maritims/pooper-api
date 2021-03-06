from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.auth import oauth2_scheme
from src.database import get_database_session, NotificationSubscription
from src.models.notification_subscription import NotificationSubscriptionRead, NotificationSubscriptionCreate
from src.models.user import UserRead
from src.services.notifications import send_notification_to_subscription
from src.services.users import get_current_user

router = APIRouter(
    prefix="/notifications",
    tags=["notifications"],
    dependencies=[Depends(oauth2_scheme)]
)


@router.post("/subscribe", response_model=NotificationSubscriptionRead, status_code=status.HTTP_201_CREATED)
def subscribe(subscription: NotificationSubscriptionCreate, session: Session = Depends(get_database_session),
              token: str = Depends(oauth2_scheme)):
    current_user: UserRead = get_current_user(session, token)

    db_subscription = NotificationSubscription(
        endpoint=subscription.endpoint,
        public_key=subscription.public_key,
        authentication_secret=subscription.authentication_secret,
        created_by_user_id=current_user.id,
        created=datetime.now(),
        updated_by_user_id=current_user.id,
        updated = datetime.now()
    )

    session.add(db_subscription)
    session.commit()
    session.refresh(db_subscription)

    return db_subscription


@router.put("/subscribe", response_model=NotificationSubscriptionRead)
def subscribe(subscription: NotificationSubscriptionCreate, session: Session = Depends(get_database_session),
              token: str = Depends(oauth2_scheme)):
    current_user = get_current_user(session, token)

    db_subscription: NotificationSubscription = session.query(NotificationSubscription)\
        .where(NotificationSubscription.endpoint == subscription.endpoint)

    if db_subscription is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subscription was not found"
        )

    db_subscription.authentication_secret = subscription.authentication_secret
    db_subscription.endpoint = subscription.endpoint
    db_subscription.public_key = subscription.public_key
    db_subscription.updated = datetime.now()
    db_subscription.updated_by_user_id = current_user.id

    session.add(db_subscription)
    session.commit()
    session.refresh(db_subscription)

    return db_subscription


@router.get("/test")
def test(session: Session = Depends(get_database_session), token: str = Depends(oauth2_scheme)):
    current_user = get_current_user(session, token)
    subscription = session.query(NotificationSubscription)\
        .where(NotificationSubscription.created_by_user_id == current_user.id).first()
    send_notification_to_subscription(subscription, "Hello!", "World!")
