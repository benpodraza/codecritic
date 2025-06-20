from uuid import uuid4
from sqlalchemy.orm import Session

from app.db.models import ScoreProviderConfig
from app.db.schemas import LintingScoreConfig, CodeStabilityScoreConfig
from app.enums.logging_enums import PROVIDER_TYPE
from app.utilities.file_management.file_utils import get_file_manager, FILETYPE

fm = get_file_manager()

SCORES = [
    {
        "id": 1,
        "filename": "score_providers/linting_score_provider.py",
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
        "filename": "score_providers/code_stability_score_provider.py",
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
    for entry in SCORES:
        guid = str(uuid4())
        dest_filename = f"{guid}.py"
        content = fm.load(FILETYPE.SEED_SOURCE, entry["filename"])
        fm.save(FILETYPE.EXTENSION, dest_filename, content)

        score = ScoreProviderConfig(
            id=entry["id"],
            guid=guid,
            name=entry["name"],
            description=entry["description"],
            config=entry["config"],
            artifact_path=dest_filename,
            tags=entry["tags"],
            provider_type=PROVIDER_TYPE.SCORE,
        )

        db_session.add(score)

    db_session.commit()
    print("✅ Seeded score providers successfully.")
