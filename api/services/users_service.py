import logging
from sqlalchemy.orm import Session
from models import models 
from schemas import schemas
from sqlalchemy.exc import SQLAlchemyError
from core.security import HashHelper
from fastapi import HTTPException, status

#Logger
logger = logging.getLogger(__name__)

def create_new_user(db: Session, user_data: schemas.UserCreate):

    user_exists = db.query(models.User).filter(models.User.email == user_data.email).first()

    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado"
        )

    try:
    # 1. Hasheamos la password que viene del esquema
        hashed_pass = HashHelper.get_password_hash(user_data.password)
    
    # 2. Creamos el modelo de DB
        db_user = models.User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_pass
        )
    
    # 3. Guardamos
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al crear usuario: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al crear usuario"
        )
    




