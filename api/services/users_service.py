import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from models import user_model
from schemas.user_schema import UserCreate
from core.security import get_password_hash

logger = logging.getLogger(__name__)


# 🔹 Excepciones de dominio
class UserAlreadyExistsError(Exception):
    pass

class UserNotFoundError(Exception):
    pass


# 🔹 CREATE
def create_user(db: Session, user_data: UserCreate):

    existing_user = (
        db.query(user_model.User)
        .filter(user_model.User.email == user_data.email)
        .first()
    )

    if existing_user:
        raise UserAlreadyExistsError("Email already registered")

    hashed_password = get_password_hash(user_data.password)

    db_user = user_model.User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password
    )

    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    except SQLAlchemyError:
        db.rollback()
        logger.exception("Database error creating user")
        raise


# 🔹 READ
def get_user_by_id(db: Session, user_id: int):
    user = (
        db.query(user_model.User)
        .filter(user_model.User.id == user_id)
        .first()
    )

    if not user:
        raise UserNotFoundError("User not found")

    return user