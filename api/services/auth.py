from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from api.models.user import User
from api.models.refresh_token import RefreshToken
from api.schemas.auth import TokenResponse
from api.core.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
    verify_refresh_token
)
from api.core.settings import settings
import logging

logger = logging.getLogger(__name__)

class InvalidCredentialsError(Exception):
    pass


def authenticate_user(email: str, password_plain: str, db: Session) -> TokenResponse:
    try:
        db_user = db.query(User).filter(User.email == email).first()
    except SQLAlchemyError:
        logger.exception("Database error authenticating user")
        raise

    if not db_user or not verify_password(password_plain, db_user.hashed_password):
        raise InvalidCredentialsError("Invalid credentials")

    access_token = create_access_token(data={"sub": str(db_user.id)})
    refresh_token_str = create_refresh_token(data={"sub": str(db_user.id)})

    db_token = RefreshToken(
        token=refresh_token_str,
        user_id=db_user.id,
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    db.add(db_token)
    db.commit()

    return TokenResponse(access_token=access_token, refresh_token=refresh_token_str)


def refresh_access_token(refresh_token_str: str, db: Session) -> TokenResponse:
    payload = verify_refresh_token(refresh_token_str)
    if not payload:
        raise InvalidCredentialsError("Invalid refresh token")

    try:
        db_token = db.query(RefreshToken).filter(
            RefreshToken.token == refresh_token_str,
            RefreshToken.revoked == False
        ).first()
    except SQLAlchemyError:
        logger.exception("Database error fetching refresh token")
        raise

    if not db_token:
        raise InvalidCredentialsError("Refresh token revoked or not found")

    # Rotar — revocar el viejo, emitir uno nuevo
    db_token.revoked = True

    new_refresh = create_refresh_token(data={"sub": payload["sub"]})
    new_access = create_access_token(data={"sub": payload["sub"]})

    new_db_token = RefreshToken(
        token=new_refresh,
        user_id=db_token.user_id,
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    db.add(new_db_token)
    db.commit()

    return TokenResponse(access_token=new_access, refresh_token=new_refresh)
