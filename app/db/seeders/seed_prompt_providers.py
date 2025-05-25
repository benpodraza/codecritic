from uuid import uuid4
from pathlib import Path
import shutil
from sqlalchemy.orm import Session
from app.db.models import PromptProviderConfig

CURRENT_DIR = Path(__file__).resolve().parent
SEED_FILES_DIR = CURRENT_DIR / "files/prompt_providers"
PROJECT_ROOT = SEED_FILES_DIR.parent.parent.parent.parent.parent

EXTENSIONS_DIR = PROJECT_ROOT / "extensions"

GENERATORS = [
    ("basic_prompt_provider.py", "Basic Prompt Provider", "Returns a simple prompt response.", ["default"]),
]

def seed_prompt_providers(db_session: Session):
    EXTENSIONS_DIR.mkdir(parents=True, exist_ok=True)

    for filename, name, description, tags in GENERATORS:
        guid = str(uuid4())
        source_file = SEED_FILES_DIR / filename
        dest_file = EXTENSIONS_DIR / f"{guid}.py"

        if not source_file.exists():
            raise FileNotFoundError(f"Prompt provider script not found: {source_file}")

        shutil.copy(source_file, dest_file)

        config = PromptProviderConfig(
            guid=guid,
            name=name,
            description=description,
            artifact_path=guid,
            tags=tags
        )

        db_session.add(config)

    db_session.commit()
    print("Seeded prompt provider configurations successfully.")
