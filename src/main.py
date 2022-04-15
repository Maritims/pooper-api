import logging.config
from logging import getLogger

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .logging_config import logging_config
from .database import create_db_and_tables, seed_users
from .routers import animals, auth, events, users, notifications, trips, conditions
from .settings_manager import settingsManager
from .services.tenants import get_tenant, get_tenants, is_valid_tenant

logging.config.dictConfig(logging_config)
log = getLogger(__name__)


app = FastAPI(
    title="Pooper API",
    version="1.0.1",
    contact={
        "name": "Martin Severin Steffensen",
        "url": "https://github.com/Maritims",
        "email": "maritim@gmail.com"
    }
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settingsManager.get_setting('CLIENT_BASE_URL').split(','),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(animals.router)
app.include_router(auth.router)
app.include_router(conditions.router)
app.include_router(events.router)
app.include_router(notifications.router)
app.include_router(trips.router)
app.include_router(users.router)


@app.middleware("http")
async def verify_tenant(request: Request, call_next):
    tenant = get_tenant(request)
    if is_valid_tenant(tenant) is True:
        response = await call_next(request)
    else:
        response = JSONResponse(status_code=401, content={'reason': 'Invalid tenant'})
    return response
