# app/db/seeders/seed_controller_providers.py

from uuid import uuid4
from pathlib import Path
import shutil
from sqlalchemy.orm import Session
from app.db.models import ControllerProviderConfig

SEED_FILES_DIR = Path(__file__).parent / "files/controller_providers"
PROJECT_ROOT   = SEED_FILES_DIR.parents[4]
EXTENSIONS_DIR = PROJECT_ROOT / "extensions"

CONTROLLER_PROVIDERS = [
    {
        "id": 1,
        "filename": "preprocessing_controller_provider.py",
        "name": "preprocessing_controller",
        "description": "Runs only the preprocessing step (e.g. linting).",
        "tags": ["preprocessing", "controller"],
        "config": {
            "score_provider_id": 1,
            "systems": {
                "preprocess": 1   # ID of your linting_system_provider
            }
        }
    }
]

def seed_controller_providers(db_session: Session):
    EXTENSIONS_DIR.mkdir(parents=True, exist_ok=True)
    for entry in CONTROLLER_PROVIDERS:
        guid      = str(uuid4())
        src       = SEED_FILES_DIR / entry["filename"]
        dest      = EXTENSIONS_DIR / f"{guid}.py"
        if not src.exists():
            raise FileNotFoundError(f"Missing script: {src}")
        shutil.copy(src, dest)

        rec = ControllerProviderConfig(
            id            = entry["id"],
            guid          = guid,
            name          = entry["name"],
            description   = entry["description"],
            config        = entry["config"],
            artifact_path = dest.name,
            tags          = entry["tags"],
        )
        db_session.add(rec)
    db_session.commit()
    print("✅ Seeded controller providers")
