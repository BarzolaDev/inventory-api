from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    stock: int = 0

class ProductCreate(ProductBase):
    pass 

class Product(ProductBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True


class MovementBase(BaseModel):
    quantity: int
    type: str 

class MovementCreate(MovementBase):
    product_id: int

class MovementResponse(MovementBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

    