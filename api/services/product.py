import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError


from api.models import movement, product
from api.schemas.product import ProductCreate
from api.schemas.movement import MovementCreate
from api.utils.db_utils import commit_and_refresh

logger = logging.getLogger(__name__)


# 🔹 Excepciones de dominio
class ProductNotFoundError(Exception):
    pass


class InsufficientStockError(Exception):
    pass


# 🔹 CREATE
def create_product(db: Session, product_data: ProductCreate):
    db_product = product.Product(**product_data.model_dump())
    
    return commit_and_refresh(db, db_product, action="create_product")


# 🔹 READ
def get_products(db: Session, skip: int = 0, limit: int = 10):
    return (
        db.query(product.Product)
        .offset(skip)
        .limit(limit)
        .all()
    )


# 🔹 UPDATE (stock)
def update_stock(product_id: int, movement_data: MovementCreate, db: Session):
    try:
        product = (
            db.query(product.Product)
            .filter(product.Product.id == product_id)
            .with_for_update()
            .first()
        )

        if not product:
            raise ProductNotFoundError("Product not found")

        new_stock = product.stock + movement_data.quantity

        if new_stock < 0:
            raise InsufficientStockError("Insufficient stock")

        movement = movement.StockMovement(
            product_id=product.id,
            quantity=movement_data.quantity
        )

        product.stock = new_stock

        db.add(movement)
        db.commit()
        db.refresh(product)

        return product

    except SQLAlchemyError:
        db.rollback()
        logger.exception("Database error updating stock")
        raise


# 🔹 DELETE
def delete_product(product_id: int, db: Session):
    product = (
        db.query(product.Product)
        .filter(product.Product.id == product_id)
        .first()
    )

    if not product:
        raise ProductNotFoundError("Product not found")

    try:
        db.delete(product)
        db.commit()

    except SQLAlchemyError:
        db.rollback()
        logger.exception("Database error deleting product")
        raise


# 🔹 MOVEMENTS
def get_movements(product_id: int, db: Session):
    return (
        db.query(movement.StockMovement)
        .filter(movement.StockMovement.product_id == product_id)
        .all()
    )