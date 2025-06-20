from uuid import uuid4
from sqlalchemy.orm import Session

from app.db.models import ControllerProviderConfig
from app.enums.logging_enums import PROVIDER_TYPE
from app.enums.system_enums import SYSTEM
from app.utilities.file_management.file_utils import get_file_manager, FILETYPE

fm = get_file_manager()

CONTROLLER_PROVIDERS = [
    {
        "id": 1,
        "filename": "controller_providers/preprocessing_controller_provider.py",
        "name": "preprocessing_controller",
        "description": "Runs only the preprocessing step (e.g. linting).",
        "tags": ["preprocessing", "controller"],
        "config": {
            "components": {
                "score_provider_id": 1,
                "systems": {
                    SYSTEM.LINTING.value: 1
                }
            },
            "params": {
                "max_steps": 20
            }
        }
    }
]

def seed_controller_providers(db_session: Session):
    for entry in CONTROLLER_PROVIDERS:
        guid = str(uuid4())
        dest_filename = f"{guid}.py"
        content = fm.load(FILETYPE.SEED_SOURCE, entry["filename"])
        fm.save(FILETYPE.EXTENSION, dest_filename, content)

        rec = ControllerProviderConfig(
            id=entry["id"],
            guid=guid,
            name=entry["name"],
            description=entry["description"],
            config=entry["config"],
            artifact_path=dest_filename,
            tags=entry["tags"],
            provider_type=PROVIDER_TYPE.CONTROLLER,
        )
        db_session.add(rec)

    db_session.commit()
    print("✅ Seeded controller providers")
