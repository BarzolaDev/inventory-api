import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from api.models.user import User
from api.schemas.user import UserCreate
from api.core.security import get_password_hash
from api.utils.db_utils import commit_and_refresh

logger = logging.getLogger(__name__)


# 🔹 Excepciones de dominio
class UserAlreadyExistsError(Exception):
    pass

class UserNotFoundError(Exception):
    pass


# 🔹 CREATE
def create_user(db: Session, user_data: UserCreate):

    try:
        existing_user = (
            db.query(User)
            .filter(
                (User.email == user_data.email) |
                (User.username == user_data.username)
            )
            .first()
        )
    except SQLAlchemyError:
        logger.exception("Database error checking existing user")
        raise

    if existing_user:
        if existing_user.email == user_data.email:
            raise UserAlreadyExistsError("Email already registered")
        raise UserAlreadyExistsError("Username already registered")


    hashed_password = get_password_hash(user_data.password)

    db_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password
    )

    return commit_and_refresh(db, db_user, action="create_user")


# 🔹 READ
def get_user_by_id(db: Session, user_id: int):
    try:
        db_user = (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )
    except SQLAlchemyError:
        logger.exception("Database error fetching user by id")
        raise

    if not db_user:
        raise UserNotFoundError("User not found")

    return db_user