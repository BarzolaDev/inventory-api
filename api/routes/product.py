from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from redis.asyncio import Redis

from api.schemas.product import ProductCreate, ProductUpdate, Product
from api.schemas.movement import MovementCreate, MovementResponse

from api.db.database import get_db
from api.services import product as product_service
from api.core.depends import get_current_user
from api.core.redis_client import get_redis
from api.core.rate_limiter import rate_limit
from api.models.user import User

import logging
logger = logging.getLogger(__name__)

router = APIRouter()

# 🔹 READ
@router.get("/", response_model=list[Product])
def get_products(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 10
):
    return product_service.get_products(db=db, skip=skip, limit=limit)

# 🔹 GET BY ID
@router.get("/{product_id}", response_model=Product)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
):
    try:
        return product_service.get_product_by_id(product_id, db)
    except product_service.ProductNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

# 🔹 CREATE
@router.post("/", response_model=Product, status_code=status.HTTP_201_CREATED)
async def create_product(
    request: Request,
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    redis: Redis = Depends(get_redis)
):
    await rate_limit(request, limit=20, window=60, redis=redis)
    try:
        result = product_service.create_product(db=db, product_data=product)
        logger.info(f"Producto creado - user: {current_user.id}")
        return result
    except Exception:
        logger.error(f"Error creando producto - user: {current_user.id}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error creating product")

# 🔹 UPDATE PRODUCT
@router.patch("/{product_id}", response_model=Product)
async def update_product(
    request: Request,
    product_id: int,
    product_in: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    redis: Redis = Depends(get_redis)
):
    await rate_limit(request, limit=20, window=60, redis=redis)
    try:
        result = product_service.update_product(
            product_id=product_id,
            product_data=product_in,
            db=db
        )
        logger.info(f"Producto actualizado - product_id: {product_id} - user: {current_user.id}")
        return result
    except product_service.ProductNotFoundError as e:
        logger.warning(f"Producto no encontrado - product_id: {product_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except product_service.InvalidPriceError as e:
        logger.warning(f"Precio inválido - product_id: {product_id}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception:
        logger.error(f"Error actualizando producto - product_id: {product_id}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error updating product")

# 🔹 UPDATE STOCK
@router.post("/{product_id}/stock", response_model=Product)
async def update_product_stock(
    request: Request,
    product_id: int,
    movement: MovementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    redis: Redis = Depends(get_redis)
):
    await rate_limit(request, limit=10, window=60, redis=redis)
    try:
        result = product_service.update_stock(product_id=product_id, movement_data=movement, db=db)
        logger.info(f"Stock actualizado - product_id: {product_id} - user: {current_user.id}")
        return result
    except product_service.ProductNotFoundError as e:
        logger.warning(f"Producto no encontrado - product_id: {product_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except product_service.InsufficientStockError as e:
        logger.warning(f"Stock insuficiente - product_id: {product_id} - user: {current_user.id}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception:
        logger.error(f"Error actualizando stock - product_id: {product_id}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error updating stock")

# 🔹 DELETE
@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    request: Request,
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    redis: Redis = Depends(get_redis)
):
    await rate_limit(request, limit=5, window=60, redis=redis)
    try:
        product_service.delete_product(product_id=product_id, db=db)
        logger.warning(f"Producto eliminado - product_id: {product_id} - user: {current_user.id}")
    except product_service.ProductNotFoundError as e:
        logger.warning(f"Intento de eliminar producto inexistente - product_id: {product_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception:
        logger.error(f"Error eliminando producto - product_id: {product_id}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error deleting product")

# 🔹 MOVEMENTS
@router.get("/{product_id}/movements", response_model=list[MovementResponse])
def get_movements(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return product_service.get_movements(
        product_id=product_id,
        db=db
    )