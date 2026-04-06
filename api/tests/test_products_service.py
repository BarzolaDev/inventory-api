from services.products_service import new_product, update_stock, delete_product
from schemas.product_schema import ProductCreate
from schemas.movement_schema import MovementCreate
import pytest

from services.products_service import new_product, update_stock, delete_product
from schemas.product_schema import ProductCreate
from schemas.movement_schema import MovementCreate
import pytest


# Happy path: creación correcta de producto
def test_create_product(db):
    data = ProductCreate(name="Test", price=100, stock=10)

    product = new_product(db, data)

    assert product.id is not None
    assert product.name == "Test"
    assert product.stock == 10


# Edge case: producto no existe
def test_update_stock_product_not_found(db):
    movement = MovementCreate(quantity=5)

    with pytest.raises(ValueError, match="Product not found"):
        update_stock(999, movement, db)


# Edge case: evitar stock negativo
def test_update_stock_insufficient(db):
    product = new_product(db, ProductCreate(name="Test", price=100, stock=5))

    movement = MovementCreate(quantity=-10)

    with pytest.raises(ValueError, match="Insufficient stock"):
        update_stock(product.id, movement, db)


# Happy path: actualización correcta de stock
def test_update_stock_ok(db):
    product = new_product(db, ProductCreate(name="Test", price=100, stock=5))

    movement = MovementCreate(quantity=10)

    updated = update_stock(product.id, movement, db)

    assert updated.stock == 15


# Edge case: eliminar producto inexistente
def test_delete_product_not_found(db):
    with pytest.raises(ValueError, match="Product not found"):
        delete_product(999, db)


# Edge case: lista vacía de productos
def test_get_products_empty(db):
    from services.products_service import get_products

    products = get_products(db)

    assert products == []