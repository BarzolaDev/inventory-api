import uuid
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from api.db.database import Base


class StockMovement(Base):
    __tablename__ = "stock_movements"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    product_id = Column(
        String(36),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    quantity = Column(Integer, nullable=False)

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    product = relationship(
        "Product",
        back_populates="movements"
    )