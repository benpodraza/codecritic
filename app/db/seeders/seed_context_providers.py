from uuid import uuid4
from pathlib import Path
import shutil
from sqlalchemy.orm import Session
from app.db.models import ContextProviderConfig

SEED_FILES_DIR = Path(__file__).resolve().parent / "files/context_providers"
PROJECT_ROOT = SEED_FILES_DIR.parent.parent.parent.parent.parent
EXTENSIONS_DIR = PROJECT_ROOT / "extensions"

CONTEXT_PROVIDERS = [
    {
        "id": 1,
        "filename": "basic_context_provider.py",
        "name": "basic_context_provider",
        "description": "Returns static context for testing.",
        "tags": ["default"],
        "config": {}
    },
    {
        "id": 2,
        "filename": "linting_context_provider.py",
        "name": "linting_context_provider",
        "description": "Generates context for the linting system.",
        "tags": ["linting", "score-aware"],
        "config": {
            "score_provider_id": 1,
            "tool_provider_ids": None
        }
    }
]

def seed_context_providers(db_session: Session):
    EXTENSIONS_DIR.mkdir(parents=True, exist_ok=True)

    for entry in CONTEXT_PROVIDERS:
        guid = str(uuid4())
        dest_filename = f"{guid}.py"
        source_file = SEED_FILES_DIR / entry["filename"]
        dest_file = EXTENSIONS_DIR / dest_filename

        if not source_file.exists():
            raise FileNotFoundError(f"Context provider script not found: {source_file}")

        shutil.copy(source_file, dest_file)

        config = ContextProviderConfig(
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
    print("Seeded context provider configurations successfully.")