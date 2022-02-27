from datetime import datetime
from logging import getLogger

from sqlalchemy import Boolean, create_engine, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

from .auth import pwd_context
from .settings_manager import settingsManager

Base = declarative_base()

log = getLogger(__name__)
engine = create_engine(f"mariadb+mariadbconnector://"
                       f"{settingsManager.get_setting('MARIADB_USER')}:"
                       f"{settingsManager.get_setting('MARIADB_PASSWORD')}@"
                       f"{settingsManager.get_setting('MARIADB_SERVER')}/"
                       f"{settingsManager.get_setting('MARIADB_DATABASE')}")
SessionLocal = sessionmaker(bind=engine)


class Animal(Base):
    __tablename__ = 'animal'

    id = Column(Integer, primary_key=True)
    name = Column(String(256), nullable=False)
    created = Column(DateTime, nullable=False)
    created_by_user_id = Column(Integer, nullable=False)
    updated = Column(DateTime, nullable=False)
    updated_by_user_id = Column(DateTime, nullable=False)
    events = relationship("Event", back_populates="animal")
    notes = relationship("Note", back_populates="animal", order_by="desc(Note.created)")
    is_deactivated = Column(Boolean, nullable=False)


class Event(Base):
    __tablename__ = 'event'

    id = Column(Integer, primary_key=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    event_type = Column(String(256), nullable=False)
    animal_id = Column(Integer, ForeignKey('animal.id'))
    created = Column(DateTime, nullable=False)
    created_by_user_id = Column(Integer, ForeignKey('user.id'))
    updated = Column(DateTime, nullable=False)
    updated_by_user_id = Column(Integer)
    animal = relationship("Animal", back_populates="events")
    created_by_user = relationship("User", back_populates="events")
    rating = Column(Integer)
    trip_id = Column(Integer, nullable=True)

    @hybrid_property
    def animal_name(self):
        return self.animal.name

    @hybrid_property
    def created_by_user_name(self):
        return f"{self.created_by_user.first_name} {self.created_by_user.last_name}"


class Note(Base):
    __tablename__ = 'note'

    id = Column(Integer, primary_key=True)
    text = Column(String(256), nullable=False)
    animal_id = Column(Integer, ForeignKey('animal.id'))
    created = Column(DateTime, nullable=False)
    created_by_user_id = Column(Integer, ForeignKey('user.id'))
    created_by_user = relationship("User", viewonly=True)
    updated = Column(DateTime, nullable=False)
    updated_by_user_id = Column(Integer)
    updated_by_user = relationship("User", viewonly=True)
    animal = relationship("Animal", back_populates="notes")

    @hybrid_property
    def created_by_user_name(self):
        return f"{self.created_by_user.first_name} {self.created_by_user.last_name}"

    @hybrid_property
    def updated_by_user_name(self):
        return f"{self.updated_by_user.first_name} {self.updated_by_user.last_name}"


class Notification(Base):
    __tablename__ = 'notification'

    id = Column(Integer, primary_key=True)
    title = Column(String(256), nullable=False)
    message = Column(String(256), nullable=False)
    created = Column(DateTime, nullable=False)
    created_by_user_id = Column(Integer, ForeignKey('user.id'))
    created_by_user = relationship("User")

    @hybrid_property
    def created_by_user_name(self):
        return self.created_by_user.name


class NotificationSubscription(Base):
    __tablename__ = 'notification_subscription'

    id = Column(Integer, primary_key=True)
    endpoint = Column(String(256), nullable=False)
    public_key = Column(String(256), nullable=False)
    authentication_secret = Column(String(256), nullable=False)
    created_by_user_id = Column(Integer, ForeignKey('user.id'))
    created = Column(DateTime, nullable=False)
    updated_by_user_id = Column(Integer, ForeignKey('user.id'))
    updated = Column(DateTime, nullable=False)


class Trip(Base):
    __tablename__ = 'trip'

    id = Column(Integer, primary_key=True)
    created_by_user_id = Column(Integer, ForeignKey('user.id'))
    created_by_user = relationship("User")
    created_date = Column(DateTime, nullable=False)

    @hybrid_property
    def created_by_user_name(self):
        return f"{self.created_by_user.first_name} {self.created_by_user.last_name}"


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    first_name = Column(String(256), nullable=False)
    last_name = Column(String(256), nullable=False)
    email_address = Column(String(256), nullable=False)
    password_hash = Column(String(256), nullable=False)
    password_reset_token = Column(String(256), nullable=True)
    is_disabled = Column(Boolean, nullable=False)
    created = Column(DateTime, nullable=False)
    updated = Column(DateTime, nullable=False)
    events = relationship("Event", back_populates="created_by_user")
    trips = relationship("Trip", back_populates="created_by_user")
    home_longitude = Column(Float, nullable=True)
    home_latitude = Column(Float, nullable=True)
    color_theme = Column(String(256), nullable=True)


def create_db_and_tables():
    Base.metadata.create_all(engine)


def get_database_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def seed_users():
    log.info("Seeding users")
    email_address = "admin@pooper.online"
    session = SessionLocal()

    user = session.query(User).where(User.email_address == email_address).first()
    if user is not None:
        return

    log.info(f"Creating user with username {email_address}")

    user = User(
        first_name="Admin",
        last_name="Admin",
        email_address=email_address,
        password_hash=pwd_context.hash("admin"),
        is_disabled=False,
        created=datetime.now(),
        updated=datetime.now()
    )

    session.add(user)
    session.commit()
    session.close()
