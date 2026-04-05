from pydantic import BaseModel
from datetime import datetime

class MovementCreate(BaseModel):
    quantity: int

class MovementResponse(MovementCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True