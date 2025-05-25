from uuid import uuid4
from pathlib import Path
import shutil
from sqlalchemy.orm import Session
from app.db.models import StateProviderConfig

SEED_FILES_DIR = Path(__file__).resolve().parent / "files/state_providers"
PROJECT_ROOT = SEED_FILES_DIR.parent.parent.parent.parent.parent
EXTENSIONS_DIR = PROJECT_ROOT / "extensions"

STATE_PROVIDERS = [
    ("basic_state_provider.py", "Basic State Provider", "Simple FSM for agent progression.", ["default"], {"states": ["start", "review", "approve"]}),
]

def seed_state_providers(db_session: Session):
    EXTENSIONS_DIR.mkdir(parents=True, exist_ok=True)

    for filename, name, description, tags, config in STATE_PROVIDERS:
        guid = str(uuid4())
        source_file = SEED_FILES_DIR / filename
        dest_file = EXTENSIONS_DIR / f"{guid}.py"

        if not source_file.exists():
            raise FileNotFoundError(f"State provider script not found: {source_file}")

        shutil.copy(source_file, dest_file)

        record = StateProviderConfig(
            guid=guid,
            name=name,
            description=description,
            config=config,
            artifact_path=guid,
            tags=tags,
        )

        db_session.add(record)

    db_session.commit()
    print("Seeded state provider configurations successfully.")
