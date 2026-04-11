from pydantic import BaseModel, EmailStr, Field, ConfigDict

class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)

class UserResponse(UserBase):
    id: int
    model_config = ConfigDict(from_attributes=True)