from pydantic import BaseModel, ConfigDict
from datetime import datetime

class MovementCreate(BaseModel):
    quantity: int

class MovementResponse(MovementCreate):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)