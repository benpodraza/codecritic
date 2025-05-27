from __future__ import annotations
from typing import List
from sqlalchemy.orm import Session
from app.db.models import AgentConversationLog

def get_conversation_log(session: Session, session_id: str, system: str) -> List[str]:
    """Returns logged conversation entries for the specified session and system."""
    logs = (
        session.query(AgentConversationLog)
        .filter_by(session_id=session_id, system=system)
        .order_by(AgentConversationLog.timestamp.asc())
        .all()
    )

    return [log.content for log in logs if log.content]
