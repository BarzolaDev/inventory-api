from pydantic import BaseModel, ConfigDict, Field, field_validator
from datetime import datetime

class MovementBase(BaseModel):
    quantity: int

    @field_validator("quantity")
    @classmethod
    def quantity_not_zero(cls, v: int) -> int:
        if v == 0:
            raise ValueError("quantity must not be zero")
        return v

class MovementCreate(MovementBase):
    pass

class MovementResponse(MovementBase):
    id: int
    product_id: int  
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)