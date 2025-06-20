from uuid import uuid4
from sqlalchemy.orm import Session

from app.db.models import ProgramProviderConfig
from app.enums.controller_enums import CONTROLLER
from app.enums.logging_enums import PROVIDER_TYPE

from app.utilities.file_management.file_utils import get_file_manager, FILETYPE

fm = get_file_manager()

PROGRAM_PROVIDERS = [
    {
        "id": 1,
        "filename": "program_providers/codecritic_program_provider.py",
        "name": "codecritic_program",
        "description": "Top-level orchestration of all system controllers.",
        "tags": ["program", "codecritic"],
        "config": {
            "components": {
                "score_provider_id": 1,
                "controllers": {
                    CONTROLLER.PREPROCESSING.value: 1
                }
            },
            "params": {
                "max_steps": 20
            }
        }
    }
]

def seed_program_providers(db_session: Session):
    for entry in PROGRAM_PROVIDERS:
        guid = str(uuid4())
        dest_filename = f"{guid}.py"
        content = fm.load(FILETYPE.SEED_SOURCE, entry["filename"])
        fm.save(FILETYPE.EXTENSION, dest_filename, content)

        record = ProgramProviderConfig(
            id=entry["id"],
            guid=guid,
            name=entry["name"],
            description=entry["description"],
            config=entry["config"],
            artifact_path=dest_filename,
            tags=entry["tags"],
            provider_type=PROVIDER_TYPE.PROGRAM,
        )
        db_session.add(record)

    db_session.commit()
    print("✅ Seeded program providers")
