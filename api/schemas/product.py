from pydantic import BaseModel, ConfigDict, Field
from decimal import Decimal

class ProductBase(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    stock: int = Field(default=0, ge=0)
    unit: str = Field(min_length=1, max_length=20)
    purchase_price: Decimal = Field(ge=0, decimal_places=2)
    sale_price: Decimal = Field(ge=0, decimal_places=2)

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    """Para PATCH — todos opcionales"""
    name: str | None = Field(default=None, min_length=2, max_length=100)
    unit: str | None = Field(default=None, min_length=1, max_length=20)
    purchase_price: Decimal | None = Field(default=None, ge=0, decimal_places=2)
    sale_price: Decimal | None = Field(default=None, ge=0, decimal_places=2)

class Product(ProductBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

