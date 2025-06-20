from uuid import uuid4
from sqlalchemy.orm import Session

from app.db.models import ContextProviderConfig
from app.enums.logging_enums import PROVIDER_TYPE
from app.utilities.file_management.file_utils import get_file_manager, FILETYPE

fm = get_file_manager()

CONTEXT_PROVIDERS = [
    {
        "id": 1,
        "filename": "context_providers/basic_context_provider.py",
        "name": "basic_context_provider",
        "description": "Returns static context for testing.",
        "tags": ["default"],
        "config": {
            "components": {},
            "params": {}
        }
    },
    {
        "id": 2,
        "filename": "context_providers/linting_context_provider.py",
        "name": "linting_context_provider",
        "description": "Generates context for the linting system.",
        "tags": ["linting", "score-aware"],
        "config": {
            "components": {
                "score_provider_id": 1,
                "tool_provider_ids": None
            },
            "params": {}
        }
    }
]

def seed_context_providers(db_session: Session):
    for entry in CONTEXT_PROVIDERS:
        guid = str(uuid4())
        dest_filename = f"{guid}.py"
        content = fm.load(FILETYPE.SEED_SOURCE, entry["filename"])
        fm.save(FILETYPE.EXTENSION, dest_filename, content)

        config = ContextProviderConfig(
            id=entry["id"],
            guid=guid,
            name=entry["name"],
            description=entry["description"],
            artifact_path=dest_filename,
            tags=entry["tags"],
            config=entry["config"],
            provider_type=PROVIDER_TYPE.CONTEXT,
        )

        db_session.add(config)

    db_session.commit()
    print("✅ Seeded context provider configurations successfully.")
