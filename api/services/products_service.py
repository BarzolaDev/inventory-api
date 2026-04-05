import logging
from sqlalchemy.orm import Session
from models import product_model, stock_movement_model
from schemas import product_schema
from schemas import movement_schema

logger = logging.getLogger(__name__)


# 🔹 CREATE
def new_product(db: Session, product_data: product_schema.ProductCreate):
    try:
        db_product = product_model.Product(**product_data.model_dump())
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        return db_product
    except Exception:
        db.rollback()
        logger.exception("Error creating product")
        raise


# 🔹 READ
def get_products(db: Session, skip: int = 0, limit: int = 10):
    return db.query(product_model.Product).offset(skip).limit(limit).all()


# 🔹 UPDATE (stock)
def update_stock(product_id: int, movement_data: movement_schema.MovementCreate, db: Session):
    try:
        product = (
            db.query(product_model.Product)
            .filter(product_model.Product.id == product_id)
            .with_for_update()
            .first()
        )

        if not product:
            raise ValueError("Product not found")

        new_stock = product.stock + movement_data.quantity

        if new_stock < 0:
            raise ValueError("Insufficient stock")

        movement = stock_movement_model.StockMovement(
            product_id=product.id,
            quantity=movement_data.quantity
        )

        product.stock = new_stock

        db.add(movement)
        db.commit()
        db.refresh(product)

        return product

    except Exception:
        db.rollback()
        logger.exception("Error updating stock")
        raise


# 🔹 DELETE
def delete_product(product_id: int, db: Session):
    product = db.query(product_model.Product).filter(product_model.Product.id == product_id).first()

    if not product:
        raise ValueError("Product not found")

    db.delete(product)
    db.commit()


def get_movements(product_id: int, db: Session):
    return (
        db.query(stock_movement_model.StockMovement)
        .filter(stock_movement_model.StockMovement.product_id == product_id)
        .all()
    )