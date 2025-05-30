from uuid import uuid4
from pathlib import Path
import shutil
from sqlalchemy.orm import Session
from app.db.models import AgentEngineProviderConfig

SEED_FILES_DIR = Path(__file__).resolve().parent / "files/agent_engine_providers"
PROJECT_ROOT = SEED_FILES_DIR.parent.parent.parent.parent.parent
EXTENSIONS_DIR = PROJECT_ROOT / "extensions"

AGENT_ENGINES = [
    (1, "basic_agent_engine_provider.py", "basic_agent_engine_provider", "Returns a mock LLM response.", "mock-llm", ["default"]),
    (2, "openai_gpt4o_agent_engine_provider.py", "openai_gpt_4o_agent_engine", "Runs GPT-4o via OpenAI API.", "gpt-4o", ["openai", "production"])
]

def seed_agent_engine_providers(db_session: Session):
    EXTENSIONS_DIR.mkdir(parents=True, exist_ok=True)

    for id_, filename, name, description, model, tags in AGENT_ENGINES:
        guid = str(uuid4())
        source_file = SEED_FILES_DIR / filename
        dest_file = EXTENSIONS_DIR / f"{guid}.py"

        if not source_file.exists():
            raise FileNotFoundError(f"Agent engine script not found: {source_file}")

        shutil.copy(source_file, dest_file)

        config = AgentEngineProviderConfig(
            id=id_,
            guid=guid,
            name=name,
            description=description,
            model=model,
            config={},
            artifact_path=str(dest_file),
            tags=tags,
        )

        db_session.add(config)

    db_session.commit()
    print("Seeded agent engine configurations successfully.")
