from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime

class MovementCreate(BaseModel):
    quantity: int = Field(ne=0) 

class MovementResponse(MovementCreate):
    id: int
    product_id: int  
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)