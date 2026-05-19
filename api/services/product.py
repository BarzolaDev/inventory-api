import logging
import httpx
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from api.domain.exceptions import ProductNotFoundError, InsufficientStockError, InvalidPriceError, UnauthorizedError

from api.models.product import Product
from api.models.movement import StockMovement
from api.schemas.product import ProductCreate, ProductUpdate
from api.schemas.movement import MovementCreate
from api.utils.db_utils import commit_and_refresh

logger = logging.getLogger(__name__)

# 🔹 Create Product
def create_product(db: Session, product_data: ProductCreate, owner_id: int):
    db_product = Product(**product_data.model_dump(), owner_id=owner_id)
    return commit_and_refresh(db, db_product, action="create_product")

# 🔹 Get Products
def get_products(db: Session, skip: int = 0, limit: int = 10):
    try:
        return (
            db.query(Product)
            .offset(skip)
            .limit(limit)
            .all()
        )
    except SQLAlchemyError:
        logger.exception("Database error fetching products")
        raise

# 🔹 Product by id
def get_product_by_id(product_id: int, db: Session):
    try:
        db_product = (
            db.query(Product)
            .filter(Product.id == product_id)
            .first()
        )
    except SQLAlchemyError:
        logger.exception("Database error fetching product by id")
        raise

    if not db_product:
        raise ProductNotFoundError("Product not found")

    return db_product


# 🔹 Update (Product)
def update_product(product_id: int, product_data: ProductUpdate, db: Session, owner_id: int):
    try:
        db_product = (
            db.query(Product)
            .filter(Product.id == product_id)
            .first()
        )
    except SQLAlchemyError:
        logger.exception("Database error updating product")
        raise

    if not db_product:
        raise ProductNotFoundError("Product not found")

    if db_product.owner_id != owner_id:
        raise UnauthorizedError("Not authorized to update this product")

    changes = product_data.model_dump(exclude_unset=True)
    for field, value in changes.items():
        setattr(db_product, field, value)

    if db_product.sale_price <= db_product.purchase_price:
        raise InvalidPriceError("sale_price must be greater than purchase_price")

    return commit_and_refresh(db, db_product, action="update_product")


# 🔹 Update (stock)
def update_stock(product_id: int, movement_data: MovementCreate, db: Session, owner_id: int):
    try:
        logger.info(f"stock_lock_waiting - product_id={product_id} user={owner_id} delta={movement_data.quantity}")

        db_product = (
            db.query(Product)
            .filter(Product.id == product_id)
            .with_for_update() 
            .first()
        )

        logger.info(f"stock_lock_acquired - product_id={product_id} user={owner_id}")

        if not db_product:
            raise ProductNotFoundError("Product not found")

        if db_product.owner_id != owner_id:
            raise UnauthorizedError("Not authorized to update this product's stock")

        stock_before = db_product.stock
        new_stock = stock_before + movement_data.quantity

        if new_stock < 0:
            logger.warning(f"stock_insufficient - product_id={product_id} user={owner_id} current={stock_before} requested={movement_data.quantity}")
            raise InsufficientStockError("Insufficient stock")

        db_movement = StockMovement(
            product_id=db_product.id,
            quantity=movement_data.quantity
        )

        db_product.stock = new_stock

        db.add(db_movement)
        db.commit()
        db.refresh(db_product)

        logger.info(f"stock_updated - product_id={product_id} user={owner_id} before={stock_before} after={new_stock} delta={movement_data.quantity}")

        return db_product

    except SQLAlchemyError:
        db.rollback()
        logger.exception(f"stock_db_error - product_id={product_id} user={owner_id}")
        raise


# 🔹 DELETE 
def delete_product(product_id: int, db: Session, owner_id: int):
    try:
        db_product = (
            db.query(Product)
            .filter(Product.id == product_id)
            .first()
        )

        if not db_product:
            raise ProductNotFoundError("Product not found")

        if db_product.owner_id != owner_id:
            raise UnauthorizedError("Not authorized to delete this product")

        db.delete(db_product)
        db.commit()

    except SQLAlchemyError:
        db.rollback()
        logger.exception("Database error deleting product")
        raise


# 🔹 Movements
def get_movements(product_id: int, db: Session):
    try:
        return (
            db.query(StockMovement)
            .filter(StockMovement.product_id == product_id)
            .all()
        )
    except SQLAlchemyError:
        logger.exception("Database error fetching movements")
        raise