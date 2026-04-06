from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from schemas.product_schema import ProductCreate, Product
from schemas.movement_schema import MovementCreate, MovementResponse
from db.database import get_db
from services import products_service
from core.depends import get_current_user
from models.user_model import User

router = APIRouter()


# 🔹 READ 
@router.get("/", response_model=list[Product])
def get_products(db: Session = Depends(get_db)):
    return products_service.get_products(db=db)


# 🔹 CREATE
@router.post("/", response_model=Product)
def new_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        return products_service.new_product(db=db, product_data=product)
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Error creating product"
        )


# 🔹 UPDATE STOCK 
@router.post("/{product_id}/stock", response_model=Product)
def update_product_stock(
    product_id: int,
    movement: MovementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        return products_service.update_stock(
            product_id=product_id,
            movement_data=movement,
            db=db
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Error updating stock"
        )


# 🔹 DELETE 
@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        products_service.delete_product(product_id=product_id, db=db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# 🔹 MOVEMENTS 
@router.get("/{product_id}/movements", response_model=list[MovementResponse])
def get_movements(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return products_service.get_movements(product_id=product_id, db=db)
