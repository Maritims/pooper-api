import logging.config
from logging import getLogger

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .logging_config import logging_config
from .database import create_db_and_tables
from .routers import animals, auth, events, users

logging.config.dictConfig(logging_config)
log = getLogger(__name__)


app = FastAPI(
    title="Pooper API",
    version="0.1.0",
    contact={
        "name": "Martin Severin Steffensen",
        "url": "https://github.com/Maritims",
        "email": "maritim@gmail.com"
    }
)

origins = ["http://localhost:8080"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(animals.router)
app.include_router(auth.router)
app.include_router(events.router)
app.include_router(users.router)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()
