from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from schemas.user_schema import UserCreate, UserResponse
from schemas import auth_schema 
from services import users_service, auth_service
from db.database import get_db
from models import user_model
from core import depends

router = APIRouter()


# 🔹 REGISTER
@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    try:
        return users_service.create_new_user(db=db, user_data=user_in)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Error creating user"
        )

# 🔹 LOGIN
@router.post("/login", response_model=auth_schema.TokenResponse)
def login(user: auth_schema.LoginRequest, db: Session = Depends(get_db)):
    return auth_service.authenticate_user(
        email=user.email,
        password_plain=user.password,
        db=db
    )








