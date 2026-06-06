from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from api.db.database import get_db
from api.models.agent_decision import AgentDecision
from api.core.depends import get_current_user
from api.models.user import User
from typing import Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/")
def get_decisions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(default=50, le=200),
    decision: Optional[str] = Query(default=None)
):
    query = db.query(AgentDecision).order_by(desc(AgentDecision.timestamp))
    if decision:
        query = query.filter(AgentDecision.decision == decision)
    return query.limit(limit).all()

@router.get("/stats")
def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    total = db.query(AgentDecision).count()
    blocked = db.query(AgentDecision).filter(AgentDecision.decision == "BLOQUEADO").count()
    allowed = db.query(AgentDecision).filter(AgentDecision.decision == "NORMAL").count()
    recon = db.query(AgentDecision).filter(AgentDecision.recon_correlated == True).count()
    return {
        "total": total,
        "bloqueado": blocked,
        "normal": allowed,
        "recon_correlated": recon
    }
