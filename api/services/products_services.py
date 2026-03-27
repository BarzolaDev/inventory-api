from fastapi import HTTPException, status
from models.models import Product, StockMovement
from schemas.schemas import StockUpdate
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)

def new_product(db: Session, product_data):
    db_product = Product(**product_data.model_dump())
    try:
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        return db_product
    except Exception as e:
        logger.error(f"Error en new_product {e}")

def get_products(db: Session, skip: int = 0, limit: int = 0):
    products = db.query(Product).offset(skip).limit(limit).all()
    return products

def update_stock(product_id: int, stock_update: StockUpdate, db: Session):
    product = db.query(Product).with_for_update().filter(Product.id == product_id).first() 

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail = f'El producto con id {product_id} no existe')

    new_stock = stock_update.stock + product.stock

    if new_stock < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Stock insuficiente para realizar la operación'
        )
   
    movement = StockMovement(
    product_id = product.id,
    quantity = stock_update.stock
    )
    try:
        product.stock = new_stock
        db.add(movement)
        db.commit()
        db.refresh(product)
        return product
    except Exception as e:
        db.rollback()
        logger.error(f"Error subiendo stock: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='No se pudo registrar el movimiento'
        )
        
    

def get_movements(product_id: int, db: Session):
    db_stock_movements = db.query(StockMovement).filter(
                            StockMovement.product_id == product_id
                            ).all()
    return db_stock_movements