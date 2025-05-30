from uuid import uuid4
from pathlib import Path
import shutil
from sqlalchemy.orm import Session
from app.db.models import PromptProviderConfig

CURRENT_DIR = Path(__file__).resolve().parent
SEED_FILES_DIR = CURRENT_DIR / "files/prompt_providers"
PROJECT_ROOT = SEED_FILES_DIR.parent.parent.parent.parent.parent

EXTENSIONS_DIR = PROJECT_ROOT / "extensions"

PROVIDERS = [
    {
        "id": 1,
        "filename": "basic_prompt_provider.py",
        "name": "basic_prompt_provider",
        "description": "Returns a simple prompt response.",
        "tags": ["default"],
        "config": {}
    },
    {
        "id": 2,
        "filename": "linting_prompt_provider.py",
        "name": "linting_prompt_provider",
        "description": "Combines linting system and agent prompts.",
        "tags": ["linting", "codequality"],
        "config": {
            "agent_prompt_id": 2,
            "system_prompt_id": 2,
            "context_provider_id": 2
        }
    }
]


def seed_prompt_providers(db_session: Session):
    EXTENSIONS_DIR.mkdir(parents=True, exist_ok=True)

    for entry in PROVIDERS:
        guid = str(uuid4())
        dest_filename = f"{guid}.py"
        source_file = SEED_FILES_DIR / entry["filename"]
        dest_file = EXTENSIONS_DIR / dest_filename

        if not source_file.exists():
            raise FileNotFoundError(f"Prompt provider script not found: {source_file}")

        shutil.copy(source_file, dest_file)

        config = PromptProviderConfig(
            id=entry["id"],
            guid=guid,
            name=entry["name"],
            description=entry["description"],
            config=entry["config"],
            artifact_path=dest_filename,
            tags=entry["tags"]
        )

        db_session.add(config)

    db_session.commit()
    print("Seeded prompt provider configurations successfully.")