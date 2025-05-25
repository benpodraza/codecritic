from uuid import uuid4
from pathlib import Path
import shutil
from sqlalchemy.orm import Session
from app.db.models import SystemProviderConfig

SEED_FILES_DIR = Path(__file__).resolve().parent / "files/system_providers"
PROJECT_ROOT = SEED_FILES_DIR.parent.parent.parent.parent
EXTENSIONS_DIR = PROJECT_ROOT / "extensions"

SYSTEM_PROVIDERS = [
    ("basic_system_provider.py", "Basic System Provider", "Simple FSM built on state providers.", ["default"], {"states": ["start", "validate", "complete"]}),
]

def seed_system_providers(db_session: Session):
    EXTENSIONS_DIR.mkdir(parents=True, exist_ok=True)

    for filename, name, description, tags, config in SYSTEM_PROVIDERS:
        guid = str(uuid4())
        source_file = SEED_FILES_DIR / filename
        dest_file = EXTENSIONS_DIR / f"{guid}.py"

        if not source_file.exists():
            raise FileNotFoundError(f"System provider script not found: {source_file}")

        shutil.copy(source_file, dest_file)

        record = SystemProviderConfig(
            guid=guid,
            name=name,
            description=description,
            config=config,
            artifact_path=guid,
            tags=tags,
        )

        db_session.add(record)

    db_session.commit()
    print("Seeded system provider configurations successfully.")
