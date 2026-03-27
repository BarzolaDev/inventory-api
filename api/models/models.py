from sqlalchemy import Column, Integer, String, ForeignKey
from db.database import Base
from sqlalchemy import DateTime
from datetime import datetime, timezone

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key = True, index=True)
    name = Column(String)
    stock = Column(Integer)

class StockMovement(Base):
    __tablename__ = "stock_movements"

    id = Column(Integer, primary_key= True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer)
    created_at = Column(DateTime, default= lambda: datetime.now(timezone.utc))
