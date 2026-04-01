from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from schemas import schemas
from services import users_service
from db.database import get_db

router = APIRouter()

@router.post("/", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    # El router NO sabe hashear, solo llama al que sabe
    return users_service.create_new_user(db=db, user_data=user_in)

