from pydantic import BaseModel, ConfigDict, Field, field_validator
from datetime import datetime

class MovementCreate(BaseModel):
    quantity: int

    @field_validator("quantity")
    @classmethod
    def quantity_not_zero(cls, v: int) -> int:
        if v == 0:
            raise ValueError("quantity must not be zero")
        return v

class MovementResponse(MovementCreate):
    id: int
    product_id: int  
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)