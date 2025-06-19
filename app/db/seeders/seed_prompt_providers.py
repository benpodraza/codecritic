from uuid import uuid4
from sqlalchemy.orm import Session

from app.db.models import PromptProviderConfig
from app.enums.logging_enums import PROVIDER_TYPE
from app.utilities.file_management.file_utils import get_file_manager, FILETYPE

fm = get_file_manager()

PROVIDERS = [
    {
        "id": 1,
        "filename": "prompt_providers/basic_prompt_provider.py",
        "name": "basic_prompt_provider",
        "description": "Returns a simple prompt response.",
        "tags": ["default"],
        "config": {
            "components": {},
            "params": {}
        }
    },
    {
        "id": 2,
        "filename": "prompt_providers/linting_prompt_provider.py",
        "name": "linting_prompt_provider",
        "description": "Combines linting system and agent prompts.",
        "tags": ["linting", "codequality"],
        "config": {
            "components": {
                "agent_prompt_id": 2,
                "system_prompt_id": 2,
                "context_provider_id": 2
            },
            "params": {}
        }
    }
]

def seed_prompt_providers(db_session: Session):
    for entry in PROVIDERS:
        guid = str(uuid4())
        dest_filename = f"{guid}.py"
        content = fm.load(FILETYPE.SEED_SOURCE, entry["filename"])
        fm.save(FILETYPE.EXTENSION, dest_filename, content)

        config = PromptProviderConfig(
            id=entry["id"],
            guid=guid,
            name=entry["name"],
            description=entry["description"],
            config=entry["config"],
            artifact_path=dest_filename,
            tags=entry["tags"],
            provider_type=PROVIDER_TYPE.PROMPT, 
        )

        db_session.add(config)

    db_session.commit()
    print("✅ Seeded prompt provider configurations successfully.")
