from sqlalchemy import Column, Integer, String, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from api.db.database import Base

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    stock = Column(Integer, default=0, nullable=False)
    purchase_price = Column(Numeric(10,2), nullable=False)
    sale_price = Column(Numeric(10,2), nullable=False)
    unit = Column(String, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="products")
    movements = relationship(
        "StockMovement",
        back_populates="product",
        cascade="all, delete-orphan"
    )