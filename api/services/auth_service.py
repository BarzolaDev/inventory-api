from sqlalchemy.orm import Session
from models import models 
from fastapi import HTTPException, status
from core.security import create_access_token, get_password_hash, verify_password

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
