from enum import Enum


class AGENT_ENGINE_MODEL(str, Enum):
    MOCK = "mock-llm"
    GPT_4O = "gpt-4o"
    GEMINI_1_5_PRO = "gemini-1.5-pro"
    CLAUDE_3_SONNET = "claude-3-sonnet"
