from pydantic import BaseModel

class ProductBase(BaseModel):
    name: str
    stock: int = 0

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int

    class Config:
        from_attributes = True


