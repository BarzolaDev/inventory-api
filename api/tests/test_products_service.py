from services.products_service import (
    create_product,
    update_stock,
    delete_product,
    get_products,
    ProductNotFoundError,
    InsufficientStockError
)

from schemas.product_schema import ProductCreate
from schemas.movement_schema import MovementCreate

import pytest


# 🔹 CREATE
def test_create_product(db):
    data = ProductCreate(name="Test", stock=10)

    product = create_product(db, data)

    assert product.id is not None
    assert product.name == "Test"
    assert product.stock == 10


# 🔹 UPDATE - product not found
def test_update_stock_product_not_found(db):
    movement = MovementCreate(quantity=5)

    with pytest.raises(ProductNotFoundError):
        update_stock(999, movement, db)


# 🔹 UPDATE - insufficient stock
def test_update_stock_insufficient(db):
    product = create_product(db, ProductCreate(name="Test", stock=5))

    movement = MovementCreate(quantity=-10)

    with pytest.raises(InsufficientStockError):
        update_stock(product.id, movement, db)


# 🔹 UPDATE - ok
def test_update_stock_ok(db):
    product = create_product(db, ProductCreate(name="Test", stock=5))

    movement = MovementCreate(quantity=10)

    updated = update_stock(product.id, movement, db)

    assert updated.stock == 15


# 🔹 DELETE - product not found
def test_delete_product_not_found(db):
    with pytest.raises(ProductNotFoundError):
        delete_product(999, db)


# 🔹 READ - empty list
def test_get_products_empty(db):
    products = get_products(db)

    assert products == []