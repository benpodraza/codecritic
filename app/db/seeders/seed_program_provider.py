from uuid import uuid4
from pathlib import Path
import shutil
from sqlalchemy.orm import Session
from app.db.models import OrchestratorProviderConfig, ProgramProviderConfig

SEED_PROGRAM_FILES_DIR = Path(__file__).resolve().parent / "files/programs"
PROJECT_ROOT = SEED_PROGRAM_FILES_DIR.parent.parent.parent.parent.parent
EXTENSIONS_DIR = PROJECT_ROOT / "extensions"

PROGRAM_PROVIDERS = [
    ("basic_program_provider.py", "Basic Program Provider", "Simple FSM composed of orchestrators.", ["default"], {"states": ["start", "stage1", "stage2", "complete"]}),
]

def seed_program_providers(db_session: Session):
    EXTENSIONS_DIR.mkdir(parents=True, exist_ok=True)

    for filename, name, description, tags, config in PROGRAM_PROVIDERS:
        guid = str(uuid4())
        source_file = SEED_PROGRAM_FILES_DIR / filename
        dest_file = EXTENSIONS_DIR / f"{guid}.py"
        if not source_file.exists():
            raise FileNotFoundError(f"Program provider script not found: {source_file}")
        shutil.copy(source_file, dest_file)
        record = ProgramProviderConfig(
            guid=guid,
            name=name,
            description=description,
            config=config,
            artifact_path=guid,
            tags=tags,
        )
        db_session.add(record)

    db_session.commit()
    print("Seeded program provider configurations successfully.")
