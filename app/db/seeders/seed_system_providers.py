from uuid import uuid4
from pathlib import Path
import shutil
from sqlalchemy.orm import Session
from app.db.models import SystemProviderConfig

SEED_FILES_DIR = Path(__file__).resolve().parent / "files/system_providers"
PROJECT_ROOT = SEED_FILES_DIR.parent.parent.parent.parent.parent
EXTENSIONS_DIR = PROJECT_ROOT / "extensions"

SYSTEM_PROVIDERS = [
    {
        "id": 1,
        "filename": "linting_system_provider.py",
        "name": "linting_system_provider",
        "description": "System to iteratively lint and evaluate Python code.",
        "tags": ["linting", "system"],
        "config": {
            "states": {
                "generate": 1,     
                "discriminate": 2  
            }
        }
    }
]

def seed_system_providers(db_session: Session):
    EXTENSIONS_DIR.mkdir(parents=True, exist_ok=True)

    for entry in SYSTEM_PROVIDERS:
        guid = str(uuid4())
        source_file = SEED_FILES_DIR / entry["filename"]
        dest_filename = f"{guid}.py"
        dest_file = EXTENSIONS_DIR / dest_filename

        if not source_file.exists():
            raise FileNotFoundError(f"System provider script not found: {source_file}")

        shutil.copy(source_file, dest_file)

        record = SystemProviderConfig(
            id=entry["id"],
            guid=guid,
            name=entry["name"],
            description=entry["description"],
            config=entry["config"],
            artifact_path=dest_filename,
            tags=entry["tags"],
        )

        db_session.add(record)

    db_session.commit()
    print("Seeded system provider configurations successfully.")
