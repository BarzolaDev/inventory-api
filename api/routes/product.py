from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.schemas.product import ProductCreate, Product
from api.schemas.movement import MovementCreate, MovementResponse

from api.db.database import get_db
from api.services import product as product_service
from api.core.depends import get_current_user
from api.models.user import User

router = APIRouter()


# 🔹 READ
@router.get("/", response_model=list[Product])
async def get_products(db: Session = Depends(get_db)):
    return product_service.get_products(db=db)


# 🔹 CREATE
@router.post("/", response_model=Product, status_code=status.HTTP_201_CREATED)
async def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        return product_service.create_product(
            db=db,
            product_data=product
        )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating product"
        )


# 🔹 UPDATE STOCK
@router.post("/{product_id}/stock", response_model=Product)
async def update_product_stock(
    product_id: int,
    movement: MovementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        return product_service.update_stock(
            product_id=product_id,
            movement_data=movement,
            db=db
        )

    except product_service.ProductNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

    except product_service.InsufficientStockError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating stock"
        )


# 🔹 DELETE
@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        product_service.delete_product(product_id=product_id, db=db)

    except product_service.ProductNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting product"
        )


# 🔹 MOVEMENTS
@router.get("/{product_id}/movements", response_model=list[MovementResponse])
async def get_movements(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return product_service.get_movements(
        product_id=product_id,
        db=db
    )