import logging
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)


def commit_and_refresh(db, obj, action: str = "operation"):
    try:
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj
    except SQLAlchemyError:
        db.rollback()
        logger.exception(f"Database error during {action}")
        raise
