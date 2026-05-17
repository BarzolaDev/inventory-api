from fastapi import APIRouter, Depends, HTTPException, status, Request  
from fastapi.security import OAuth2PasswordRequestForm 
from sqlalchemy.orm import Session

from api.schemas.user import UserCreate, UserResponse
from api.schemas.auth import TokenResponse, RefreshTokenRequest
from api.services import auth, user
from api.db.database import get_db
from api.core.rate_limiter import rate_limit 

import logging
logger = logging.getLogger(__name__)

router = APIRouter()


# 🔹 REGISTER
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    request: Request,     
    user_in: UserCreate,
    db: Session = Depends(get_db)
):
    await rate_limit(request, limit=10, window=3600) 
    try:
        result = user.create_user(db=db, user_data=user_in)
        logger.info(f"Usuario registrado - email: {user_in.email} - IP: {request.client.host}")
        return result
    except user.UserAlreadyExistsError as e:
        logger.warning(f"Intento de registro duplicado - email: {user_in.email} - IP: {request.client.host}")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except Exception:
        logger.error(f"Error en registro - email: {user_in.email}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


# 🔹 LOGIN
@router.post("/login", response_model=TokenResponse)
async def login(  
    request: Request,     
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    await rate_limit(request, limit=5, window=60)  
    try:
        result = await auth.authenticate_user(email=form_data.username, password_plain=form_data.password, db=db)
        logger.info(f"Login exitoso - email: {form_data.username} - IP: {request.client.host}")
        return result
    except auth.InvalidCredentialsError:
        logger.warning(f"Login fallido - email: {form_data.username} - IP: {request.client.host}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials", headers={"WWW-Authenticate": "Bearer"})


# 🔹 REFRESH TOKEN
@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(  
    request: Request,     
    body: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    await rate_limit(request, limit=20, window=60) 
    try:
        result = await auth.refresh_access_token(body.refresh_token, db)
        logger.info(f"Token refreshed - IP: {request.client.host}")
        return result
    except auth.InvalidCredentialsError:
        logger.warning(f"Refresh token inválido - IP: {request.client.host}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")


