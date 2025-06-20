# app/db/seeders/seed_session_configs.py

from sqlalchemy.orm import Session
from app.db.models import SessionConfig

SESSION_CONFIGS = [
    {
        "id": 1,
        "program_provider_id": 1,
        "name": "codecritic_test_session",
        "description": "Test session for program 1",
        "environment_type": "experiment",
        "tags": ["test", "experiment"]
    }
]

def seed_session_configs(db_session: Session):
    for sess in SESSION_CONFIGS:
        record = SessionConfig(
            id               = sess["id"],
            program_provider_id = sess["program_provider_id"],
            name             = sess["name"],
            description      = sess["description"],
            environment_type = sess["environment_type"],
            tags             = sess["tags"],
        )
        db_session.add(record)

    db_session.commit()
    print("✅ Seeded session configs")
