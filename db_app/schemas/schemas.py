from pydantic import BaseModel
from datetime import datetime

class ProductCreate(BaseModel): 
    name: str
    stock: int

class ProductPatch(BaseModel):
    stock: int

class MovementResponse(BaseModel):
    quantity: int
    created_at: datetime

    class Config:
        from_attributes = True