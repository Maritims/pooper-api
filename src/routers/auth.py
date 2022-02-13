import json
from datetime import datetime, timedelta
from logging import getLogger

import jwt
from fastapi import APIRouter, status, Depends, HTTPException, Form
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..auth import pwd_context, ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM
from ..database import get_database_session, User
from ..models.user import UserRead
from ..services.email import EmailService
from ..settings_manager import settingsManager

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

log = getLogger(__name__)


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class PasswordResetResponse(BaseModel):
    success: bool


class PasswordResetConfirmation(BaseModel):
    token: str
    new_password: str
    new_password_repeated: str

    def __init__(self, token: str = Form(...), new_password: str = Form(...), new_password_repeated: str = Form(...)):
        super().__init__(token, new_password, new_password_repeated)


@router.post("/token", response_model=LoginResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_database_session)):
    email_address = form_data.username
    user: User = session.query(User).where(User.email_address == email_address).first()

    credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid credentials"
        )

    if user is None:
        log.warning(f"Someone attempted to log in with username {email_address} but no user with this username exists.")
        raise credentials_exception

    if not pwd_context.verify(form_data.password, user.password_hash):
        log.warning(f"Someone attempted to log in with username {email_address} but supplied invalid credentials")
        raise credentials_exception

    token = jwt.encode({
        "sub": user.email_address,
        "exp": datetime.utcnow() + timedelta(ACCESS_TOKEN_EXPIRE_MINUTES),
        "user": json.dumps(UserRead(**user.__dict__).__dict__, default=str)
    }, settingsManager.get_setting("API_SECRET_AUTH_KEY"), algorithm=ALGORITHM)
    return LoginResponse(access_token=token)


@router.post("/reset-password", response_model=PasswordResetResponse)
def reset_password(email_address: str = Form(...), session: Session = Depends(get_database_session)):
    user: User = session.query(User).where(User.email_address == email_address).first()

    if user is None:
        return

    token = jwt.encode({
        "sub": user.email_address,
        "exp": datetime.now() + timedelta(days=1)
    }, settingsManager.get_setting("API_SECRET_AUTH_KEY"), algorithm=ALGORITHM)
    user.password_reset_token = token
    user.updated = datetime.now()

    session.add(user)
    session.commit()
    session.refresh(user)

    password_reset_link = f'{settingsManager.get_setting("CLIENT_BASE_URL")}/confirm-password-reset' \
                          f'?token={user.password_reset_token}'
    email_service = EmailService(settingsManager.get_setting("SENDGRID_API_KEY"))
    response = email_service.send_email(
        from_email_address=settingsManager.get_setting("SENDER_EMAIL_ADDRESS"),
        to_email_address=email_address,
        subject='Reset your password',
        message=f'Click the following link to finish resetting your password: '
                f'<a href="{password_reset_link}">{password_reset_link}</a>'
    )

    return PasswordResetResponse(success=response)


@router.post("/confirm-password-reset", response_model=PasswordResetResponse)
def confirm_password_reset(token: str = Form(...),
                           new_password: str = Form(...),
                           new_password_repeated: str = Form(...),
                           session: Session = Depends(get_database_session)):
    if new_password != new_password_repeated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Passwords must match"
        )

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f"Invalid credentials"
    )

    user: User = session.query(User).where(User.password_reset_token == token).first()

    if user is None:
        raise credentials_exception

    payload = jwt.decode(token, settingsManager.get_setting("API_SECRET_AUTH_KEY"), algorithms=ALGORITHM)
    email_address = payload['sub']

    if user.email_address != email_address:
        raise credentials_exception

    user.password_hash = pwd_context.hash(new_password)
    user.password_reset_token = None
    user.updated = datetime.now()

    session.add(user)
    session.commit()

    expiration = payload['exp']
    return PasswordResetResponse(success=True)

