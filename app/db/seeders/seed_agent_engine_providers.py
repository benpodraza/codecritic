from uuid import uuid4
from sqlalchemy.orm import Session

from app.db.models import AgentEngineProviderConfig
from app.enums.logging_enums import PROVIDER_TYPE
from app.utilities.file_management.file_utils import get_file_manager, FILETYPE

fm = get_file_manager()

AGENT_ENGINES = [
    {
        "id": 1,
        "filename": "agent_engine_providers/basic_agent_engine_provider.py",
        "name": "basic_agent_engine_provider",
        "description": "Returns a mock LLM response.",
        "model": "mock-llm",
        "tags": ["default"],
        "cost_per_1k_tokens": 0.0
    },
    {
        "id": 2,
        "filename": "agent_engine_providers/openai_gpt4o_agent_engine_provider.py",
        "name": "openai_gpt_4o_agent_engine",
        "description": "Runs GPT-4o via OpenAI API.",
        "model": "gpt-4o",
        "tags": ["openai", "production"],
        "cost_per_1k_tokens": 0.005
    },
    {
        "id": 3,
        "filename": "agent_engine_providers/gemini_1_5_pro_agent_engine_provider.py",
        "name": "gemini_1_5_pro_agent_engine",
        "description": "Runs Gemini 1.5 Pro via Google AI API.",
        "model": "gemini-1.5-pro",
        "tags": ["google", "production"],
        "cost_per_1k_tokens": 0.007
    },
    {
        "id": 4,
        "filename": "agent_engine_providers/claude_3_sonnet_agent_engine_provider.py",
        "name": "claude_3_sonnet_agent_engine",
        "description": "Runs Claude 3 Sonnet via AWS Bedrock.",
        "model": "claude-3-sonnet",
        "tags": ["aws", "bedrock", "production"],
        "cost_per_1k_tokens": 0.003
    },
]

def seed_agent_engine_providers(db_session: Session):
    for entry in AGENT_ENGINES:
        guid = str(uuid4())
        dest_filename = f"{guid}.py"
        content = fm.load(FILETYPE.SEED_SOURCE, entry["filename"])
        fm.save(FILETYPE.EXTENSION, dest_filename, content)

        config = AgentEngineProviderConfig(
            id=entry["id"],
            guid=guid,
            name=entry["name"],
            description=entry["description"],
            model=entry["model"],
            config={},
            cost_per_1k_tokens=entry["cost_per_1k_tokens"],
            artifact_path=dest_filename,
            tags=entry["tags"],
            provider_type=PROVIDER_TYPE.AGENT_ENGINE,
        )

        db_session.add(config)

    db_session.commit()
    print("✅ Seeded agent engine configurations successfully.")
