from sqlalchemy.orm import Session
from models import user_model
from schemas.auth_schema import TokenResponse
from fastapi import HTTPException, status
from core.security import create_access_token, verify_password

def authenticate_user(email: str, password_plain: str, db: Session) -> dict :

    user = db.query(user_model.User).filter(user_model.User.email == email).first()
    
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
    
    return TokenResponse(
    access_token=access_token,
    token_type="bearer"
    )

