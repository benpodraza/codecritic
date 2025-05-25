from uuid import uuid4
from pathlib import Path
import shutil
from sqlalchemy.orm import Session
from app.db.models import OrchestratorProviderConfig

SEED_FILES_DIR = Path(__file__).resolve().parent / "files/orchestrators"
PROJECT_ROOT = SEED_FILES_DIR.parent.parent.parent.parent.parent
EXTENSIONS_DIR = PROJECT_ROOT / "extensions"

ORCHESTRATOR_PROVIDERS = [
    ("basic_orchestrator_provider.py", "Basic Orchestrator Provider", "Simple FSM composed of systems.", ["default"], {"states": ["init", "train", "evaluate"]}),
]

def seed_orchestrator_providers(db_session: Session):
    EXTENSIONS_DIR.mkdir(parents=True, exist_ok=True)

    for filename, name, description, tags, config in ORCHESTRATOR_PROVIDERS:
        guid = str(uuid4())
        source_file = SEED_FILES_DIR / filename
        dest_file = EXTENSIONS_DIR / f"{guid}.py"
        if not source_file.exists():
            raise FileNotFoundError(f"Orchestrator provider script not found: {source_file}")
        shutil.copy(source_file, dest_file)
        record = OrchestratorProviderConfig(
            guid=guid,
            name=name,
            description=description,
            config=config,
            artifact_path=guid,
            tags=tags,
        )
        db_session.add(record)

    db_session.commit()
    print("Seeded orchestrator provider configurations successfully.")
