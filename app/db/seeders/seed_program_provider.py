from uuid import uuid4
from pathlib import Path
import shutil
from sqlalchemy.orm import Session
from app.db.models import ProgramProviderConfig
from app.enums.fsm_enums import STATE  # ✅ Import your FSM state enum

SEED_FILES_DIR = Path(__file__).resolve().parent / "files/program_providers"
PROJECT_ROOT   = SEED_FILES_DIR.parents[4]
EXTENSIONS_DIR = PROJECT_ROOT / "extensions"

PROGRAM_PROVIDERS = [
    {
        "id": 1,
        "filename": "codecritic_program_provider.py",
        "name": "codecritic_program",
        "description": "Top-level orchestration of all system controllers.",
        "tags": ["program", "codecritic"],
        "config": {
            "score_provider_id": 1,
            "controllers": {
                STATE.PREPROCESS.value: 1  # ✅ Enum-safe
            }
        }
    }
]

def seed_program_providers(db_session: Session):
    EXTENSIONS_DIR.mkdir(parents=True, exist_ok=True)

    for entry in PROGRAM_PROVIDERS:
        guid = str(uuid4())
        src  = SEED_FILES_DIR / entry["filename"]
        dst  = EXTENSIONS_DIR / f"{guid}.py"

        if not src.exists():
            raise FileNotFoundError(f"❌ Missing file: {src}")

        shutil.copy(src, dst)

        record = ProgramProviderConfig(
            id            = entry["id"],
            guid          = guid,
            name          = entry["name"],
            description   = entry["description"],
            config        = entry["config"],
            artifact_path = dst.name,
            tags          = entry["tags"],
        )
        db_session.add(record)

    db_session.commit()
    print("✅ Seeded program providers")
