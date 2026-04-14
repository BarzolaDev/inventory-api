from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from api.models.user import User
from api.schemas.auth import TokenResponse
from api.core.security import create_access_token, verify_password
import logging


logger = logging.getLogger(__name__)

class InvalidCredentialsError(Exception):
    pass

def authenticate_user(email: str, password_plain: str, db: Session) -> TokenResponse:
    try:
        db_user = (
        db.query(User)
        .filter(User.email == email)
        .first()
        )
    except SQLAlchemyError:
        logger.exception("Database error autehnticating user")
        raise

    if not db_user or not verify_password(password_plain, db_user.hashed_password):
        raise InvalidCredentialsError("Invalid credentials")

    access_token = create_access_token(
        data={"sub": str(db_user.id)}
    )

    return TokenResponse(
        access_token=access_token
    )

