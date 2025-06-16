from __future__ import annotations
from typing import List
from sqlalchemy.orm import Session
from app.db.models import AgentConversationLog

def get_conversation_log(session: Session, session_id: str, file_log_id: str) -> List[str]:
    """Returns logged conversation entries for the specified session and file_log_id."""
    logs = (
        session.query(AgentConversationLog)
        .filter_by(session_id=session_id, file_log_id=file_log_id)
        .order_by(AgentConversationLog.timestamp.asc())
        .all()
    )

    return [log.content for log in logs if log.content]
