from sqlalchemy import Boolean, create_engine, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy.ext.hybrid import hybrid_property
from logging import getLogger

Base = declarative_base()

log = getLogger(__name__)
engine = create_engine("mariadb+mariadbconnector://pooper:pooper@127.0.0.1/pooper")
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
