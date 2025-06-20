from uuid import uuid4
from sqlalchemy.orm import Session

from app.db.models import AgentProviderConfig
from app.enums.logging_enums import PROVIDER_TYPE
from app.utilities.file_management.file_utils import get_file_manager, FILETYPE

fm = get_file_manager()

AGENT_PROVIDERS = [
    {
        "id": 1,
        "filename": "agent_providers/basic_agent_provider.py",
        "name": "basic_agent_provider",
        "description": "Returns a hardcoded result.",
        "agent_type": "basic",
        "tags": ["test"],
        "config": {
            "components": {},
            "params": {}
        }
    },
    {
        "id": 2,
        "filename": "agent_providers/linting_generator_agent_provider.py",
        "name": "linting_generator_agent_provider",
        "description": "Runs GPT-4o to generate linting corrections.",
        "agent_type": "generator",
        "tags": ["linting", "generator"],
        "config": {
            "components": {
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
            },
            "params": {}
        }
    },
    {
        "id": 3,
        "filename": "agent_providers/linting_discriminator_agent_provider.py",
        "name": "linting_discriminator_agent_provider",
        "description": "Evaluates generator output for acceptance.",
        "agent_type": "discriminator",
        "tags": ["linting", "discriminator"],
        "config": {
            "components": {
                "score_provider_id": 1
            },
            "params": {}
        }
    },
    {
        "id": 4,
        "filename": "agent_providers/code_stability_agent_provider.py",
        "name": "code_stability_agent_provider",
        "description": "Rejects output if code is not parseable, importable, compilable, or type-valid.",
        "agent_type": "stability",
        "tags": ["stability"],
        "config": {
            "components": {
                "score_provider_id": 2
            },
            "params": {}
        }
    }
]

def seed_agent_providers(db_session: Session):
    for entry in AGENT_PROVIDERS:
        guid = str(uuid4())
        dest_filename = f"{guid}.py"
        content = fm.load(FILETYPE.SEED_SOURCE, entry["filename"])
        fm.save(FILETYPE.EXTENSION, dest_filename, content)

        config = AgentProviderConfig(
            id=entry["id"],
            guid=guid,
            name=entry["name"],
            description=entry["description"],
            artifact_path=dest_filename,
            tags=entry["tags"],
            config=entry["config"],
            agent_type=entry["agent_type"],
            provider_type=PROVIDER_TYPE.AGENT,
        )

        db_session.add(config)

    db_session.commit()
    print("✅ Seeded agent provider configurations successfully.")
