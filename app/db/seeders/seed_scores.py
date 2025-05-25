from uuid import uuid4
from pathlib import Path
import shutil
from sqlalchemy.orm import Session
from app.db.models import ScoreProviderConfig

CURRENT_DIR = Path(__file__).resolve().parent
SEED_FILES_DIR = CURRENT_DIR / "files/score_providers"
PROJECT_ROOT = SEED_FILES_DIR.parent.parent.parent.parent.parent
EXTENSIONS_DIR = PROJECT_ROOT / "extensions"

SCORES = [
    ("lint_score.py", "Lint Score Provider", "Scores lint compliance.", {}),
]

def seed_score_providers(db_session: Session):
    EXTENSIONS_DIR.mkdir(parents=True, exist_ok=True)

    for filename, name, description, _ in SCORES:
        guid = str(uuid4())
        source_file = SEED_FILES_DIR / filename
        dest_file = EXTENSIONS_DIR / f"{guid}.py" 

        if not source_file.exists():
            raise FileNotFoundError(f"Score provider script not found: {source_file}")

        shutil.copy(source_file, dest_file)

        score = ScoreProviderConfig(
            guid=guid,
            name=name,
            description=description,
            artifact_path=guid 
        )

        db_session.add(score)

    db_session.commit()
    print("Seeded score providers successfully.")
