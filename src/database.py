from datetime import datetime
from logging import getLogger
from fastapi import Body, Depends, Request

from sqlalchemy import Boolean, create_engine, Column, DateTime, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, declared_attr
from sqlmodel import Session

from .auth import pwd_context
from .settings_manager import settingsManager

Base = declarative_base()

log = getLogger(__name__)


class BaseMixin(object):
    @declared_attr
    def __tablename__(self):
        return self.__name__.lower()

    id = Column(Integer, primary_key=True)
    created = Column(DateTime, nullable=False)
    created_by_user_id = Column(Integer, nullable=False)
    updated = Column(DateTime, nullable=False)
    updated_by_user_id = Column(Integer, nullable=False)


class Animal(BaseMixin, Base):
    __tablename__ = 'animal'

    name = Column(String(256), nullable=False)
    is_deactivated = Column(Boolean, nullable=False)

    tracked_conditions = relationship(
        "Condition",
        primaryjoin="and_(Animal.id == Condition.animal_id,"
                    " Animal.id == AnimalConditionTypeAssociation.animal_id,"
                    " Condition.condition_type == AnimalConditionTypeAssociation.condition_type)"
    )
    tracked_events = relationship(
        "Event",
        back_populates="animal",
        primaryjoin="and_(Animal.id == Event.animal_id,"
                    " Animal.id == AnimalEventTypeAssociation.animal_id,"
                    " Event.event_type == AnimalEventTypeAssociation.event_type)"
    )
    notes = relationship("Note", back_populates="animal", order_by="desc(Note.created)")
    tracked_condition_types = relationship("AnimalConditionTypeAssociation")
    tracked_event_types = relationship("AnimalEventTypeAssociation")
    weight_history = relationship("AnimalWeight", lazy="noload")


class AnimalEventTypeAssociation(Base):
    __tablename__ = 'animal_event_type_association'

    id = Column(Integer, primary_key=True)
    animal_id = Column(Integer, ForeignKey('animal.id', ondelete='cascade'))
    event_type = Column(String(256), nullable=False)
    created = Column(DateTime, nullable=False)
    created_by_user_id = Column(Integer, ForeignKey("user.id"))
    updated = Column(DateTime, nullable=False)
    updated_by_user_id = Column(Integer, ForeignKey("user.id"))


class AnimalConditionTypeAssociation(Base):
    __tablename__ = 'animal_condition_association'

    id = Column(Integer, primary_key=True)
    animal_id = Column(Integer, ForeignKey('animal.id', ondelete='cascade'))
    condition_type = Column(String(256), nullable=False)
    created = Column(DateTime, nullable=False)
    created_by_user_id = Column(Integer, ForeignKey('user.id'))
    updated = Column(DateTime, nullable=False)
    updated_by_user_id = Column(Integer, ForeignKey('user.id'))


class AnimalWeight(BaseMixin, Base):
    animal_id = Column(Integer, ForeignKey('animal.id', ondelete='cascade'))
    weight_in_grams = Column(Float, nullable=False)


class Condition(BaseMixin, Base):
    __table_args__ = (UniqueConstraint('animal_id', 'condition_type'),)

    animal_id = Column(Integer, ForeignKey('animal.id', ondelete='cascade'))
    animal = relationship("Animal", back_populates="tracked_conditions")
    condition_type = Column(String(256), nullable=False)
    is_enabled = Column(Boolean, nullable=False)


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
    animal = relationship("Animal", back_populates="tracked_events")
    animal_event_type_association = relationship(
        "AnimalEventTypeAssociation",
        primaryjoin="and_(Event.event_type == AnimalEventTypeAssociation.event_type,"
                    " Event.animal_id == AnimalEventTypeAssociation.animal_id)",
        foreign_keys=[event_type, animal_id],
        viewonly=True
    )
    created_by_user = relationship("User", back_populates="events")
    rating = Column(Integer)
    trip_id = Column(Integer, nullable=True)

    @hybrid_property
    def animal_name(self):
        return self.animal.name

    @hybrid_property
    def created_by_user_name(self):
        return f"{self.created_by_user.first_name} {self.created_by_user.last_name}"

    @hybrid_property
    def is_tracked(self):
        return True if self.animal_event_type_association is not None else False


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


def get_database_engine(database: str):
    return create_engine(f"mariadb+mariadbconnector://"
        f"{settingsManager.get_setting('MARIADB_USER')}:"
        f"{settingsManager.get_setting('MARIADB_PASSWORD')}@"
        f"{settingsManager.get_setting('MARIADB_SERVER')}/"
        f"{database}")


def get_database_session_maker(database: str):
    engine = get_database_engine(database)
    sessionMaker = sessionmaker(bind = engine)
    return sessionMaker


def get_database_session(request: Request) -> Session:
    database = 'pooper'
    
    # Get db from hostname.
    if request.base_url.hostname.find('.') != -1:
        database = request.base_url.hostname.split('.')[0]

    # Get db from headers.
    if 'HTTP_X_DATABASE' in request.headers:
        database = request.headers['HTTP_X_DATABASE']

    # Ensure database and tables are created and seeded with users now that we know the database name.
    create_db_and_tables(database)
    seed_users(database)

    session_maker = get_database_session_maker(database)
    session = session_maker()

    try:
        yield session
    finally:
        session.close()


def create_db_and_tables(database: str):
    engine = get_database_engine(database)
    Base.metadata.create_all(engine)


def seed_users(database: str):
    log.info("Seeding users")
    email_address = "admin@pooper.online"
    session_maker = get_database_session_maker(database)
    session = session_maker()

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
