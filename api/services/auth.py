from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from api.models.user import User
from api.schemas.auth import TokenResponse
from api.core.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
    verify_refresh_token
)
from api.core.redis_client import get_redis
from api.core.settings import settings
import logging

logger = logging.getLogger(__name__)

class InvalidCredentialsError(Exception):
    pass


async def authenticate_user(email: str, password_plain: str, db: Session) -> TokenResponse:
    try:
        db_user = db.query(User).filter(User.email == email).first()
    except SQLAlchemyError:
        logger.exception("Database error authenticating user")
        raise

    if not db_user or not verify_password(password_plain, db_user.hashed_password):
        raise InvalidCredentialsError("Invalid credentials")

    access_token = create_access_token(data={"sub": str(db_user.id)})
    refresh_token_str = create_refresh_token(data={"sub": str(db_user.id)})

    # Guardar en Redis con TTL automático
    redis = await get_redis()
    ttl = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    await redis.set(f"refresh_token:{refresh_token_str}", str(db_user.id), ex=ttl)

    return TokenResponse(access_token=access_token, refresh_token=refresh_token_str)


async def refresh_access_token(refresh_token_str: str, db: Session) -> TokenResponse:
    payload = verify_refresh_token(refresh_token_str)
    if not payload:
        raise InvalidCredentialsError("Invalid refresh token")

    redis = await get_redis()
    user_id = await redis.get(f"refresh_token:{refresh_token_str}")

    if not user_id:
        raise InvalidCredentialsError("Refresh token revoked or not found")

    # Rotar — borrar el viejo, emitir uno nuevo
    await redis.delete(f"refresh_token:{refresh_token_str}")

    new_refresh = create_refresh_token(data={"sub": payload["sub"]})
    new_access = create_access_token(data={"sub": payload["sub"]})

    ttl = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    await redis.set(f"refresh_token:{new_refresh}", user_id, ex=ttl)

    return TokenResponse(access_token=new_access, refresh_token=new_refresh)