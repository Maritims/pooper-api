import os
from unittest import mock, TestCase

from sqlalchemy.orm import Session


@mock.patch.dict(os.environ, {
    "CLIENT_BASE_URL": "mock client base url",
    "API_SECRET_AUTH_KEY": "mock api secret auth key",
    "SENDER_EMAIL_ADDRESS": "mock sender email address",
    "SENDGRID_API_KEY": "mock sendgrid api key",
    "MARIADB_USER": "pooper",
    "MARIADB_PASSWORD": "pooper",
    "MARIADB_DATABASE": "pooper",
    "MARIADB_SERVER": "127.0.0.1",
    "VAPID_PUBLIC_KEY": "mock vapid public key",
    "VAPID_PRIVATE_KEY": "mock vapid private key"
})
class NotificationsTest(TestCase):
    @staticmethod
    def test_send_notification_to_users(self):
        """
        Send notification to all users.
        """
        from src.database import SessionLocal
        from src.services.notifications import send_notification_to_users
        session: Session = SessionLocal()
        send_notification_to_users("Hello", "World", [4], session, "mock token")

    @staticmethod
    def test_send_notification_to_subscription(self):
        """
        Send a notification
        :return:
        """
        from src.database import NotificationSubscription, SessionLocal
        from src.services.notifications import send_notification_to_subscription

        session: Session = SessionLocal()
        subscription = session.query(NotificationSubscription)\
            .where(NotificationSubscription.created_by_user_id == 4)\
            .first()
        send_notification_to_subscription(subscription, "Hello!", "World!")