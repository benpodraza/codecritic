from uuid import uuid4
from pathlib import Path
import shutil
from sqlalchemy.orm import Session
from app.db.models import AgentEngineProviderConfig

SEED_FILES_DIR = Path(__file__).resolve().parent / "files/agent_engine_providers"
PROJECT_ROOT = SEED_FILES_DIR.parent.parent.parent.parent.parent
EXTENSIONS_DIR = PROJECT_ROOT / "extensions"

AGENT_ENGINES = [
    {
        "id": 1,
        "filename": "basic_agent_engine_provider.py",
        "name": "basic_agent_engine_provider",
        "description": "Returns a mock LLM response.",
        "model": "mock-llm",
        "tags": ["default"],
        "cost_per_1k_tokens": 0.0
    },
    {
        "id": 2,
        "filename": "openai_gpt4o_agent_engine_provider.py",
        "name": "openai_gpt_4o_agent_engine",
        "description": "Runs GPT-4o via OpenAI API.",
        "model": "gpt-4o",
        "tags": ["openai", "production"],
        "cost_per_1k_tokens": 0.005
    },
    {
        "id": 3,
        "filename": "gemini_1_5_pro_agent_engine_provider.py",
        "name": "gemini_1_5_pro_agent_engine",
        "description": "Runs Gemini 1.5 Pro via Google AI API.",
        "model": "gemini-1.5-pro",
        "tags": ["google", "production"],
        "cost_per_1k_tokens": 0.007
    },
    {
        "id": 4,
        "filename": "claude_3_sonnet_agent_engine_provider.py",
        "name": "claude_3_sonnet_agent_engine",
        "description": "Runs Claude 3 Sonnet via AWS Bedrock.",
        "model": "claude-3-sonnet",
        "tags": ["aws", "bedrock", "production"],
        "cost_per_1k_tokens": 0.003
    },
]

def seed_agent_engine_providers(db_session: Session):
    EXTENSIONS_DIR.mkdir(parents=True, exist_ok=True)

    for entry in AGENT_ENGINES:
        guid = str(uuid4())
        source_file = SEED_FILES_DIR / entry["filename"]
        dest_file = EXTENSIONS_DIR / f"{guid}.py"

        if not source_file.exists():
            raise FileNotFoundError(f"Agent engine script not found: {source_file}")

        shutil.copy(source_file, dest_file)

        config = AgentEngineProviderConfig(
            id=entry["id"],
            guid=guid,
            name=entry["name"],
            description=entry["description"],
            model=entry["model"],
            config={},
            cost_per_1k_tokens=entry["cost_per_1k_tokens"],
            artifact_path=str(dest_file),
            tags=entry["tags"],
        )

        db_session.add(config)

    db_session.commit()
    print("✅ Seeded agent engine configurations successfully.")
