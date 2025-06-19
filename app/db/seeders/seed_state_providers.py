from uuid import uuid4
from pathlib import Path
import shutil
from sqlalchemy.orm import Session
from app.db.models import StateProviderConfig
from app.enums.logging_enums import PROVIDER_TYPE
from app.enums.state_enums import STATE
from app.enums.agent_enums import AGENT

SEED_FILES_DIR = Path(__file__).resolve().parent / "files/state_providers"
PROJECT_ROOT = SEED_FILES_DIR.parent.parent.parent.parent.parent
EXTENSIONS_DIR = PROJECT_ROOT / "extensions"

STATE_PROVIDERS = [
    {
        "id": 1,
        "filename": "linting_generator_state_provider.py",
        "name": "LintingGeneratorStateProvider",
        "description": "Runs the generator agent in its own FSM wrapper.",
        "tags": ["linting", "generator"],
        "config": {
            "components": {
                "score_provider_id": 1,
                "agents": {
                    AGENT.GENERATOR.value: 2
                }
            },
            "params": {
                "max_steps": 20
            }
        }
    },
    {
        "id": 2,
        "filename": "linting_discriminator_state_provider.py",
        "name": "LintingDiscriminatorStateProvider",
        "description": "Runs the discriminator agent in its own FSM wrapper.",
        "tags": ["linting", "discriminator"],
        "config": {
            "components": {
                "score_provider_id": 1,
                "agents": {
                    AGENT.DISCRIMINATOR.value: 3
                }
            },
            "params": {
                "max_steps": 20
            }
        }
    },
    {
        "id": 3,
        "filename": "code_stability_state_provider.py",
        "name": "CodeStabilityStateProvider",
        "description": "Gates code based on parse, compile, import, and static validation success.",
        "tags": ["stability"],
        "config": {
            "components": {
                "score_provider_id": 1,
                "agents": {
                    AGENT.STABILITY.value: 4
                }
            },
            "params": {
                "max_steps": 20
            }
        }
    }
]

def seed_state_providers(db_session: Session):
    EXTENSIONS_DIR.mkdir(parents=True, exist_ok=True)

    for entry in STATE_PROVIDERS:
        guid = str(uuid4())
        source_file = SEED_FILES_DIR / entry["filename"]
        dest_filename = f"{guid}.py"
        dest_file = EXTENSIONS_DIR / dest_filename

        if not source_file.exists():
            raise FileNotFoundError(f"State provider script not found: {source_file}")

        shutil.copy(source_file, dest_file)

        record = StateProviderConfig(
            id=entry["id"],
            guid=guid,
            name=entry["name"],
            description=entry["description"],
            config=entry["config"],
            artifact_path=dest_filename,
            tags=entry["tags"],
            provider_type=PROVIDER_TYPE.STATE, 
        )

        db_session.add(record)

    db_session.commit()
    print("✅ Seeded state provider configurations successfully.")
