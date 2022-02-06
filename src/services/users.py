import jwt
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.auth import ALGORITHM
from src.database import User
from src.models.user import UserRead
from src.settings_manager import settingsManager


def get_current_user(session: Session, token: str) -> UserRead:
    payload = jwt.decode(token, settingsManager.get_setting('API_SECRET_AUTH_KEY'), algorithms=ALGORITHM)
    email_address: str = payload.get("sub")

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials"
    )

    if email_address is None:
        raise credentials_exception

    user = session.query(User).where(User.email_address == email_address).first()
    if user is None:
        raise credentials_exception

    return user
