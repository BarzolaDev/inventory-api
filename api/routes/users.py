from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from schemas import schemas
from services import users_service, auth_service
from db.database import get_db


router = APIRouter()

@router.post("/", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    return users_service.create_new_user(db=db, user_data=user_in)


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    return auth_service.authenticate_user(
        email=form_data.username, 
        password_plain=form_data.password,
        db=db
    )

