from uuid import uuid4
from pathlib import Path
import shutil
from sqlalchemy.orm import Session
from app.db.models import StateProviderConfig

SEED_FILES_DIR = Path(__file__).resolve().parent / "files/state_providers"
PROJECT_ROOT = SEED_FILES_DIR.parent.parent.parent.parent.parent
EXTENSIONS_DIR = PROJECT_ROOT / "extensions"

STATE_PROVIDERS = [
    (
        1,
        "linting_generator_state_provider.py",
        "LintingGeneratorStateProvider",
        "Runs the generator agent in its own FSM wrapper.",
        ["linting", "generator"],
        {
            "agents": {
                "generate": 2
            }
        }
    ),
    (
        2,
        "linting_discriminator_state_provider.py",
        "LintingDiscriminatorStateProvider",
        "Runs the discriminator agent in its own FSM wrapper.",
        ["linting", "discriminator"],
        {
            "agents": {
                "discriminate": 3
            }
        }
    ),
    (
        3,
        "code_stability_state_provider.py",
        "CodeStabilityStateProvider",
        "Gates code based on parse, compile, import, and static validation success.",
        ["stability"],
        {
            "agents": {
                "code_stability": 4  # Agent ID of CodeStabilityAgentProvider
            }
        }
    )
]

def seed_state_providers(db_session: Session):
    EXTENSIONS_DIR.mkdir(parents=True, exist_ok=True)

    for id, filename, name, description, tags, config in STATE_PROVIDERS:
        guid = str(uuid4())
        source_file = SEED_FILES_DIR / filename
        dest_filename = f"{guid}.py"
        dest_file = EXTENSIONS_DIR / dest_filename

        if not source_file.exists():
            raise FileNotFoundError(f"State provider script not found: {source_file}")

        shutil.copy(source_file, dest_file)

        record = StateProviderConfig(
            id=id,
            guid=guid,
            name=name,
            description=description,
            config=config,
            artifact_path=dest_filename,
            tags=tags,
        )

        db_session.add(record)

    db_session.commit()
    print("✅ Seeded state provider configurations successfully.")
