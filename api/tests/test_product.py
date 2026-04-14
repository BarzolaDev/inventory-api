from api.services.product import (
    create_product,
    get_products,
    get_product_by_id,
    update_product,
    update_stock,
    delete_product,
    get_movements,
    ProductNotFoundError,
    InsufficientStockError,
    InvalidPriceError
)

from api.schemas.product import ProductCreate, ProductUpdate
from api.schemas.movement import MovementCreate

import pytest
from decimal import Decimal


PRODUCT_DEFAULTS = dict(
    unit="kg",
    purchase_price="5.00",
    sale_price="10.00"
)


def test_create_product_ok(db):
    data = ProductCreate(name="test", stock=10, **PRODUCT_DEFAULTS)
    product = create_product(db, data)
    assert product.id is not None
    assert product.name == 'test'
    assert product.stock == 10


def test_get_product_by_id(db):
    data = ProductCreate(name="test", stock=10, **PRODUCT_DEFAULTS)
    created = create_product(db, data)

    product = get_product_by_id(created.id, db)

    assert product.id == created.id
    assert product.name == "test"


def test_get_products(db):
    create_product(db, ProductCreate(name="prod1", stock=5, **PRODUCT_DEFAULTS))
    create_product(db, ProductCreate(name="prod2", stock=8, **PRODUCT_DEFAULTS))

    products = get_products(db)

    assert len(products) == 2


def test_update_product(db):
    created = create_product(db, ProductCreate(name="old", stock=10, **PRODUCT_DEFAULTS))

    updated = update_product(created.id, ProductUpdate(name="new"), db)

    assert updated.name == "new"


def test_update_stock(db):
    created = create_product(db, ProductCreate(name="test", stock=10, **PRODUCT_DEFAULTS))

    updated = update_stock(created.id, MovementCreate(quantity=5), db)

    assert updated.stock == 15


def test_delete_product(db):
    created = create_product(db, ProductCreate(name="test", stock=10, **PRODUCT_DEFAULTS))

    delete_product(created.id, db)

    with pytest.raises(ProductNotFoundError):
        get_product_by_id(created.id, db)


def test_get_movements(db):
    created = create_product(db, ProductCreate(name="test", stock=10, **PRODUCT_DEFAULTS))
    update_stock(created.id, MovementCreate(quantity=5), db)
    update_stock(created.id, MovementCreate(quantity=-3), db)

    movements = get_movements(created.id, db)

    assert len(movements) == 2


def test_get_product_by_id(db):
    with pytest.raises(ProductNotFoundError):
        get_product_by_id(9999, db)

def test_update_stock_insufficient(db):
    created = create_product(db, ProductCreate(name="test", stock=5, **PRODUCT_DEFAULTS))

    with pytest.raises(InsufficientStockError):
        update_stock(created.id, MovementCreate(quantity=-10), db)

def test_update_stock_to_zero(db):
    created = create_product(db, ProductCreate(name="test", stock=5, **PRODUCT_DEFAULTS))

    updated = update_stock(created.id, MovementCreate(quantity=-5), db)

    assert updated.stock == 0

def test_update_product_invalid_price(db):
    created = create_product(db, ProductCreate(name="test", stock=10, **PRODUCT_DEFAULTS))

    with pytest.raises(InvalidPriceError):
        update_product(created.id, ProductUpdate(sale_price=Decimal("4.00")), db)
    
    