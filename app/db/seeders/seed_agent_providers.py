from uuid import uuid4
from pathlib import Path
import shutil
from sqlalchemy.orm import Session
from app.db.models import AgentProviderConfig

SEED_FILES_DIR = Path(__file__).resolve().parent / "files/agent_providers"
PROJECT_ROOT = SEED_FILES_DIR.parent.parent.parent.parent.parent
EXTENSIONS_DIR = PROJECT_ROOT / "extensions"

AGENT_PROVIDERS = [
    {
        "id": 1,
        "filename": "basic_agent_provider.py",
        "name": "basic_agent_provider",
        "description": "Returns a hardcoded result.",
        "tags": ["test"],
        "config": {}
    },
    {
        "id": 2,
        "filename": "linting_generator_agent_provider.py",
        "name": "linting_generator_agent_provider",
        "description": "Runs GPT-4o to generate linting corrections.",
        "tags": ["linting", "generator"],
        "config": {
            "agent_engine_provider_id": 2,
            "prompt_provider_id": 2,
            "context_provider_id": 2,
            "score_provider_id": 1,
            "tool_provider_ids": {
                "black": 1,
                "ruff": 3,
                "mypy": 5,
                "radon": 4
            }
        }
    },
    {
        "id": 3,
        "filename": "linting_discriminator_agent_provider.py",
        "name": "linting_discriminator_agent_provider",
        "description": "Evaluates generator output for acceptance.",
        "tags": ["linting", "discriminator"],
        "config": {
            "score_provider_id": 1
        }
    }
]

def seed_agent_providers(db_session: Session):
    EXTENSIONS_DIR.mkdir(parents=True, exist_ok=True)

    for entry in AGENT_PROVIDERS:
        guid = str(uuid4())
        dest_filename = f"{guid}.py"
        source_file = SEED_FILES_DIR / entry["filename"]
        dest_file = EXTENSIONS_DIR / dest_filename

        if not source_file.exists():
            raise FileNotFoundError(f"Agent provider script not found: {source_file}")

        shutil.copy(source_file, dest_file)

        config = AgentProviderConfig(
            id=entry["id"],
            guid=guid,
            name=entry["name"],
            description=entry["description"],
            artifact_path=dest_filename,
            tags=entry["tags"],
            config=entry["config"]
        )

        db_session.add(config)

    db_session.commit()
    print("Seeded agent provider configurations successfully.")
