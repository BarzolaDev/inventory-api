from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime
from api.db.database import Base
from datetime import datetime, timezone


class AgentDecision(Base):
    __tablename__ = "agent_decisions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, nullable=False)
    ip = Column(String, nullable=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    action_method = Column(String, nullable=True)
    action_path = Column(String, nullable=True)
    score = Column(Float, nullable=False)
    decision = Column(String, nullable=False)
    razones = Column(Text, nullable=True)
    adaptive_flags = Column(Text, nullable=True)
    recon_correlated = Column(Boolean, default=False)
    history_len = Column(Integer, nullable=True)
    long_history_len = Column(Integer, nullable=True)
