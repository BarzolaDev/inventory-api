from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from db.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    stock = Column(Integer, default=0)

    movements = relationship(
        "StockMovement",
        back_populates="product",
        cascade="all, delete-orphan"
    )

