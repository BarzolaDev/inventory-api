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
    product = create_product(db, data, owner_id="1")
    assert product.id is not None
    assert product.name == 'test'
    assert product.stock == 10

def test_get_product_by_id(db):
    data = ProductCreate(name="test", stock=10, **PRODUCT_DEFAULTS)
    created = create_product(db, data, owner_id="1")
    product = get_product_by_id(created.id, db, owner_id="1")
    assert product.id == created.id
    assert product.name == "test"

def test_get_products(db, owner_id="1"):
    create_product(db, ProductCreate(name="prod1", stock=5, **PRODUCT_DEFAULTS), owner_id="1")
    create_product(db, ProductCreate(name="prod2", stock=8, **PRODUCT_DEFAULTS), owner_id="1")
    products = get_products(db, owner_id="1")
    assert len(products) == 2

def test_update_product(db):
    created = create_product(db, ProductCreate(name="old", stock=10, **PRODUCT_DEFAULTS), owner_id="1")
    updated = update_product(created.id, ProductUpdate(name="new"), db, owner_id="1")
    assert updated.name == "new"

def test_update_stock(db):
    created = create_product(db, ProductCreate(name="test", stock=10, **PRODUCT_DEFAULTS), owner_id="1")
    updated = update_stock(created.id, MovementCreate(quantity=5), db, owner_id="1")
    assert updated.stock == 15

def test_delete_product(db):
    created = create_product(db, ProductCreate(name="test", stock=10, **PRODUCT_DEFAULTS), owner_id="1")
    delete_product(created.id, db, owner_id="1")
    with pytest.raises(ProductNotFoundError):
        get_product_by_id(created.id, db, owner_id="1")

def test_get_movements(db):
    created = create_product(db, ProductCreate(name="test", stock=10, **PRODUCT_DEFAULTS), owner_id="1")
    update_stock(created.id, MovementCreate(quantity=5), db, owner_id="1")
    update_stock(created.id, MovementCreate(quantity=-3), db, owner_id="1")
    movements = get_movements(created.id, db, owner_id="1")
    assert len(movements) == 2

def test_get_product_by_id_not_found(db):
    with pytest.raises(ProductNotFoundError):
        get_product_by_id(9999, db, owner_id="1")

def test_update_stock_insufficient(db):
    created = create_product(db, ProductCreate(name="test", stock=5, **PRODUCT_DEFAULTS), owner_id="1")
    with pytest.raises(InsufficientStockError):
        update_stock(created.id, MovementCreate(quantity=-10), db, owner_id="1")

def test_update_stock_to_zero(db):
    created = create_product(db, ProductCreate(name="test", stock=5, **PRODUCT_DEFAULTS), owner_id="1")
    updated = update_stock(created.id, MovementCreate(quantity=-5), db, owner_id="1")
    assert updated.stock == 0

def test_update_product_invalid_price(db):
    created = create_product(db, ProductCreate(name="test", stock=10, **PRODUCT_DEFAULTS), owner_id="1")
    with pytest.raises(InvalidPriceError):
        update_product(created.id, ProductUpdate(sale_price=Decimal("4.00")), db, owner_id="1")