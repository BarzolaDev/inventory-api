from pydantic import BaseModel, ConfigDict, Field, model_validator
from decimal import Decimal

class ProductBase(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    stock: int = Field(default=0, ge=0)
    unit: str = Field(min_length=1, max_length=20)
    purchase_price: Decimal = Field(ge=0, decimal_places=2)
    sale_price: Decimal = Field(ge=0, decimal_places=2)
    @model_validator(mode="after")
    def sale_price_must_be_grater(self):
        if self.sale_price <= self.purchase_price:
            raise ValueError("sale_price must be greater than purchase_price")
        return self

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

