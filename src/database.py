from datetime import datetime

from sqlalchemy import Boolean, create_engine, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy.ext.hybrid import hybrid_property
from logging import getLogger

from .auth import pwd_context, ALGORITHM
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
    updated = Column(DateTime, nullable=False)
    events = relationship("Event", back_populates="animal")


class Event(Base):
    __tablename__ = 'event'

    id = Column(Integer, primary_key=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    event_type = Column(String(256), nullable=False)
    animal_id = Column(Integer, ForeignKey('animal.id'))
    created = Column(DateTime, nullable=False)
    updated = Column(DateTime, nullable=False)
    animal = relationship("Animal", back_populates="events")

    @hybrid_property
    def animal_name(self):
        return self.animal.name


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


def create_db_and_tables(total_attempts: int = 0) -> bool:
    max_attempts = 10
    log.info("Attempting to create database and tables")

    if total_attempts == max_attempts:
        log.error("Giving up")
        return False

    seconds_between_attempts = 5

    try:
        Base.metadata.create_all(engine)
        return True
    except Exception as err:
        log.error("Unable to create database and tables. An exception occurred: {0}. Trying again in {1} seconds".format(
            err,
            seconds_between_attempts
        ))

    total_attempts += 1
    return create_db_and_tables(total_attempts)


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
