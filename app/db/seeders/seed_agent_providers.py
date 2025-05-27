from uuid import uuid4
from pathlib import Path
import shutil
from sqlalchemy.orm import Session
from app.db.models import AgentProviderConfig

SEED_FILES_DIR = Path(__file__).resolve().parent / "files/agent_providers"
PROJECT_ROOT = SEED_FILES_DIR.parent.parent.parent.parent.parent
EXTENSIONS_DIR = PROJECT_ROOT / "extensions"

AGENT_PROVIDERS = [
    ("basic_agent_provider.py", "basic_agent_provider", "Returns a hardcoded result.", ["test"]),
    ("linting_generator_agent_provider.py", "linting_generator_agent_provider", "Runs GPT-4o to generate linting corrections.", ["linting", "generator"]),
    ("linting_discriminator_agent_provider.py", "linting_discriminator_agent_provider", "Evaluates generator output for acceptance.", ["linting", "discriminator"])
]


def seed_agent_providers(db_session: Session):
    EXTENSIONS_DIR.mkdir(parents=True, exist_ok=True)

    for filename, name, description, tags in AGENT_PROVIDERS:
        guid = str(uuid4())
        source_file = SEED_FILES_DIR / filename
        dest_file = EXTENSIONS_DIR / f"{guid}.py"

        if not source_file.exists():
            raise FileNotFoundError(f"Agent provider script not found: {source_file}")

        shutil.copy(source_file, dest_file)

        config = AgentProviderConfig(
            guid=guid,
            name=name,
            description=description,
            config={},
            artifact_path=guid,
            tags=tags,
        )

        db_session.add(config)

    db_session.commit()
    print("Seeded agent provider configurations successfully.")
