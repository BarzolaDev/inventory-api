from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm 
from sqlalchemy.orm import Session

from api.schemas.user_schema import UserCreate, UserResponse
from api.schemas.auth_schema import TokenResponse

from api.services import users_service, auth_service
from api.db.database import get_db


router = APIRouter()


# 🔹 REGISTER
@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register_user(
    user_in: UserCreate,
    db: Session = Depends(get_db)
):
    try:
        return users_service.create_user(
            db=db,
            user_data=user_in
        )

    except users_service.UserAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


# 🔹 LOGIN
@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    try:
        return auth_service.authenticate_user(
            email=form_data.username,
            password_plain=form_data.password,
            db=db
        )

    except auth_service.InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )








