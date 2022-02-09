import json
from datetime import datetime
from logging import getLogger
from typing import List

from pywebpush import webpush, WebPushException
from sqlalchemy.orm import Session

from src.database import NotificationSubscription, User, Notification
from src.models.notification_subscription import NotificationSubscriptionRead
from src.models.user import UserRead
from src.services.users import get_current_user
from src.settings_manager import settingsManager

log = getLogger(__name__)


def send_notification_to_users(title: str, message: str, exclude_user_ids: List[int], session: Session, token: str):
    users = session.query(User).filter(User.id.not_in(exclude_user_ids)).all()

    for user in users:
        send_notification_to_user(user, title, message, session, token)


def send_notification_to_user(user: UserRead, title: str, message: str, session: Session, token: str):
    subscriptions = session.query(NotificationSubscription)\
        .where(NotificationSubscription.created_by_user_id == user.id)\
        .all()

    for subscription in subscriptions:
        send_notification_to_subscription(subscription, title, message, session, token)


def send_notification_to_subscription(
        subscription: NotificationSubscriptionRead,
        title: str,
        message: str,
        session: Session,
        token: str
):
    current_user = get_current_user(session, token)

    notification = Notification(
        title=title,
        message=message,
        created=datetime.now(),
        created_by_user_id=current_user.id,
    )
    try:
        webpush(subscription_info={
            "endpoint": subscription.endpoint,
            "keys": {
                "p256dh": subscription.public_key,
                "auth": subscription.authentication_secret
            }},
            data=json.dumps({
                "title": title,
                "message": message
            }),
            vapid_private_key=settingsManager.get_setting('VAPID_PRIVATE_KEY'),
            vapid_claims={
                "sub": "mailto:no-reply@pooper.online"
            })
    except WebPushException as ex:
        log.error("Push notification could not be sent", ex)
