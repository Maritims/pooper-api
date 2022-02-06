from pydantic import BaseModel


class NotificationSubscriptionBase(BaseModel):
    endpoint: str
    public_key: str
    authentication_secret: str


class NotificationSubscriptionCreate(NotificationSubscriptionBase):
    pass


class NotificationSubscriptionRead(NotificationSubscriptionBase):
    pass
