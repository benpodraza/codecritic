import re
from pydantic import BaseModel

from app.db.schemas import AgentEngineExtraction


def extract_code_blocks(response: str) -> AgentEngineExtraction:
    def extract_block(start: str, end: str) -> str:
        match = re.search(re.escape(start) + r"(.*?)" + re.escape(end), response, re.DOTALL)
        return match.group(1).strip() if match else ""

    content = extract_block("[CODE]", "[/CODE]")
    decision = extract_block("[AGENT_DECISION]", "[/AGENT_DECISION]") 
    log = extract_block("[CONVERSATION_LOG_ENTRY]", "[/CONVERSATION_LOG_ENTRY]")

    if not content:
        raise ValueError("Extraction failed: missing content block")

    return AgentEngineExtraction(
        content=content,
        decision=decision or "DECISION_TYPE.UNKNOWN", 
        log=log or "(no log provided)"
    )
