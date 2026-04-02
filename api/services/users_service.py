import logging
from sqlalchemy.orm import Session
from models import models 
from schemas import schemas
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from core.security import create_access_token, get_password_hash, verify_password

logger = logging.getLogger(__name__)

def create_new_user(db: Session, user_data: schemas.UserCreate):

    user_exists = db.query(models.User).filter(models.User.email == user_data.email).first()

    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado"
        )

    try:
        hashed_pass = get_password_hash(user_data.password)
    
        db_user = models.User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_pass
        )
    

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


def authenticate_user(email: str, password_plain: str, db: Session) -> dict :

    user = db.query(models.User).filter(models.User.email == email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    is_verified = verify_password(password_plain, user.hashed_password)
    
    if not is_verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }




