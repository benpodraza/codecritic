from uuid import uuid4
from pathlib import Path
import shutil
from sqlalchemy.orm import Session
from app.db.models import ScoreProviderConfig
from app.db.schemas import LintingScoreConfig, CodeStabilityScoreConfig

CURRENT_DIR = Path(__file__).resolve().parent
SEED_FILES_DIR = CURRENT_DIR / "files/score_providers"
PROJECT_ROOT = SEED_FILES_DIR.parent.parent.parent.parent.parent
EXTENSIONS_DIR = PROJECT_ROOT / "extensions"

SCORES = [
    {
        "id": 1,
        "filename": "linting_score_provider.py",
        "name": "linting_score_provider",
        "description": "Scores lint compliance.",
        "config": {
            "components": {
                "tool_provider_ids": {
                    "black": 1,
                    "ruff": 3,
                    "mypy": 5,
                    "radon": 4
                }
            },
            "params": LintingScoreConfig(
                weight_ruff=0.7,
                weight_black=0.2,
                weight_mypy=0.1,
                fail_threshold=0.75
            ).model_dump()
        },
        "tags": ["linting"]
    },
    {
        "id": 2,
        "filename": "code_stability_score_provider.py",
        "name": "code_stability_score_provider",
        "description": "Ensures code is structurally and syntactically safe for downstream use.",
        "config": {
            "components": {},
            "params": CodeStabilityScoreConfig(
                failure_penalty=0.25,
                diff_penalty=0.3,
                test_weight=0.25,
                coverage_weight=0.2
            ).model_dump()
        },
        "tags": ["stability", "safety"]
    }
]

def seed_score_providers(db_session: Session):
    EXTENSIONS_DIR.mkdir(parents=True, exist_ok=True)

    for entry in SCORES:
        guid = str(uuid4())
        dest_filename = f"{guid}.py"
        source_file = SEED_FILES_DIR / entry["filename"]
        dest_file = EXTENSIONS_DIR / dest_filename

        if not source_file.exists():
            raise FileNotFoundError(f"Score provider script not found: {source_file}")

        shutil.copy(source_file, dest_file)

        score = ScoreProviderConfig(
            id=entry["id"],
            guid=guid,
            name=entry["name"],
            description=entry["description"],
            config=entry["config"],
            artifact_path=dest_filename,
            tags=entry["tags"]
        )

        db_session.add(score)

    db_session.commit()
    print("Seeded score providers successfully.")
