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
    stock: int = 0

class ProductCreate(ProductBase):
    pass 

class Product(ProductBase):
    id: int

    class Config:
        from_attributes = True

class MovementCreate(BaseModel):
    quantity: int

class MovementResponse(MovementCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

    