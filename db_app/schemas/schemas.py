from pydantic import BaseModel

class ProductCreate(BaseModel): 
    name: str
    stock: int

class ProductPatch(BaseModel):
    stock: int
