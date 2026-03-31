from fastapi import HTTPException, status 
from models import models
from schemas import schemas 
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)

def new_product(db: Session, product_data):
    db_product = models.Product(**product_data.model_dump())
    try:
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        return db_product
    except Exception as e:
        db.rollback()
        logger.error(f"Error en new_product {e}")

def get_products(db: Session, skip: int = 0, limit: int = 10):
    products = db.query(models.Product).offset(skip).limit(limit).all()
    return products

def update_stock(product_id: int, movement_data: schemas.MovementCreate, db: Session):
    try:
        # El portero bloquea la fila
        product = db.query(models.Product).with_for_update().filter(schemas.Product.id == product_id).first() 

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'El producto con id {product_id} no existe'
            )

        # Usamos .quantity que es como lo llamaste en el Schema
        new_stock = product.stock + movement_data.quantity

        if new_stock < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Stock insuficiente para realizar la operación'
            )
   
        # Creamos el registro del movimiento
        movement = models.StockMovement(
            product_id = product.id,
            quantity = movement_data.quantity,
            type = movement_data.type  # ¡No te olvides del tipo!
        )

        product.stock = new_stock
        db.add(movement)
        db.commit()
        db.refresh(product)
        return product
    
    except HTTPException as he: 
        db.rollback()
        raise he
    except Exception as e:
        db.rollback()
        logger.error(f"Error actualizando stock: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='No se pudo registrar el movimiento'
        )
        
def get_movements(product_id: int, db: Session):
    db_stock_movements = db.query(models.StockMovement).filter(
                            models.StockMovement.product_id == product_id
                            ).all()
    return db_stock_movements