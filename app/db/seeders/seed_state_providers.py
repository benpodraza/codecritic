from uuid import uuid4
from sqlalchemy.orm import Session

from app.db.models import StateProviderConfig
from app.enums.logging_enums import PROVIDER_TYPE
from app.enums.agent_enums import AGENT
from app.utilities.file_management.file_utils import get_file_manager, FILETYPE

fm = get_file_manager()

STATE_PROVIDERS = [
    {
        "id": 1,
        "filename": "state_providers/linting_generator_state_provider.py",
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
        "filename": "state_providers/linting_discriminator_state_provider.py",
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
        "filename": "state_providers/code_stability_state_provider.py",
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
    for entry in STATE_PROVIDERS:
        guid = str(uuid4())
        dest_filename = f"{guid}.py"
        content = fm.load(FILETYPE.SEED_SOURCE, entry["filename"])
        fm.save(FILETYPE.EXTENSION, dest_filename, content)

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
