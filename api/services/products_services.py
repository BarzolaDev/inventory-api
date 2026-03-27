from fastapi import HTTPException, status
from models.models import Product, StockMovement
from sqlalchemy.orm import Session
from schemas.schemas import ProductCreate, StockUpdate, MovementResponse
from db.database import get_db

def new_product(db, product_data):
    db_product = Product(name=product_data.name, stock=product_data.stock)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def get_products(db):
    products = db.query(Product).all()
    return products

def update_stock(product_id: int, stock_update: StockUpdate, db):
    product = db.query(Product).filter(Product.id == product_id).first() 

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
        quantity = stock_update.stock,
    )
    db.add(movement)

    product.stock = new_stock

    db.commit()
    db.refresh(product)

    return product

def get_movements(product_id: int, db):
    db_stock_movements = db.query(StockMovement).filter(
                            StockMovement.product_id == product_id
                            ).all()
    return db_stock_movements