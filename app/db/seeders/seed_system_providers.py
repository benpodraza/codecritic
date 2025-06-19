from uuid import uuid4
from sqlalchemy.orm import Session

from app.db.models import SystemProviderConfig
from app.enums.logging_enums import PROVIDER_TYPE
from app.enums.state_enums import STATE
from app.enums.system_enums import SYSTEM
from app.utilities.file_management.file_utils import get_file_manager, FILETYPE

fm = get_file_manager()

SYSTEM_PROVIDERS = [
    {
        "id": 1,
        "filename": "system_providers/linting_system_provider.py",
        "name": "linting_system_provider",
        "description": "System to iteratively lint and evaluate Python code.",
        "system_type": SYSTEM.LINTING.value,
        "tags": ["linting", "system"],
        "config": {
            "components": {
                "score_provider_id": 1,
                "states": {
                    STATE.GENERATE.value: 1,
                    STATE.DISCRIMINATE.value: 2,
                    STATE.CODE_STABILITY.value: 3
                }
            },
            "params": {
                "max_steps": 20
            }
        }
    }
]

def seed_system_providers(db_session: Session):
    for entry in SYSTEM_PROVIDERS:
        guid = str(uuid4())
        dest_filename = f"{guid}.py"
        content = fm.load(FILETYPE.SEED_SOURCE, entry["filename"])
        fm.save(FILETYPE.EXTENSION, dest_filename, content)

        record = SystemProviderConfig(
            id=entry["id"],
            guid=guid,
            name=entry["name"],
            description=entry["description"],
            system_type=entry["system_type"],
            config=entry["config"],
            artifact_path=dest_filename,
            tags=entry["tags"],
            provider_type=PROVIDER_TYPE.SYSTEM,
        )

        db_session.add(record)

    db_session.commit()
    print("✅ Seeded system provider configurations successfully.")
