from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from schemas.schemas import ProductCreate, MovementResponse, MovementCreate, Product
from models import models
from db.database import get_db
from services import products_services
from core.depends import get_current_user 

router = APIRouter()

router = APIRouter()

@router.post("/", response_model=Product)
def new_product(product: ProductCreate, db: Session = Depends(get_db)):
    return products_services.new_product(db=db, product_data=product)

@router.get("/", response_model=list[Product])
def get_products(db: Session = Depends(get_db)):
    return products_services.get_products(db=db)

@router.post("/{product_id}/stock", response_model=Product)
def update_product_stock(product_id: int, movement: MovementCreate, db: Session = Depends(get_db)):
    return products_services.update_stock(product_id=product_id, movement_data=movement, db=db)

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    products_services.delete_product(product_id=product_id, db=db)

@router.get("/{product_id}/movements", response_model=list[MovementResponse])
def get_movements(product_id: int, db: Session = Depends(get_db)):
    return products_services.get_movements(product_id=product_id, db=db)