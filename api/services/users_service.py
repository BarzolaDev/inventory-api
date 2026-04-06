import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models import user_model
from schemas.user_schema import UserCreate 
from core.security import get_password_hash

logger = logging.getLogger(__name__)

def create_new_user(db: Session, user_data: UserCreate):
    try:
        user_exists = (
            db.query(user_model.User)
            .filter(user_model.User.email == user_data.email)
            .first()
        )

        if user_exists:
            raise ValueError("Email already registered")

        hashed_pass = get_password_hash(user_data.password)

        db_user = user_model.User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_pass
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        return db_user

    except SQLAlchemyError:
        db.rollback()
        logger.exception("Database error creating user")
        raise

    except Exception:
        db.rollback()
        logger.exception("Unexpected error creating user")
        raise


def get_user_by_id(db: Session, user_id: int):
    return db.query(user_model.User).filter(user_model.User.id == user_id).first()