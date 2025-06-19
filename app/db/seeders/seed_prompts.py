from uuid import uuid4
from sqlalchemy.orm import Session

from app.db.models import AgentPrompt, SystemPrompt
from app.enums.system_enums import SYSTEM
from app.utilities.file_management.file_utils import get_file_manager, FILETYPE

fm = get_file_manager()

AGENT_PROMPT_FILES = [
    {
        "id": 1,
        "name": "generate",
        "filename": "prompts/basic_agent_prompt.txt",
        "description": "Prompt for basic code generation.",
        "tags": ["linting", "generator"]
    },
    {
        "id": 2,
        "name": "linting_generator_agent",
        "filename": "prompts/linting_generator_agent_prompt.txt",
        "description": "Prompt for linting generator agent.",
        "tags": ["linting", "generator"]
    }
]

SYSTEM_PROMPT_FILES = [
    {
        "id": 1,
        "name": "format",
        "filename": "prompts/default_system_prompt.txt",
        "system_type": SYSTEM.LINTING,
        "description": "Default prompt for formatting tasks.",
        "tags": ["formatting", "default"]
    },
    {
        "id": 2,
        "name": "linting_system",
        "filename": "prompts/linting_system_prompt.txt",
        "system_type": SYSTEM.LINTING,
        "description": "System prompt governing the linting subsystem.",
        "tags": ["linting", "system"]
    }
]

def seed_prompts(db_session: Session):
    for entry in AGENT_PROMPT_FILES:
        guid = str(uuid4())
        dest_filename = f"{guid}.txt"
        content = fm.load(FILETYPE.SEED_SOURCE, entry["filename"])
        fm.save(FILETYPE.EXTENSION, dest_filename, content)

        prompt = AgentPrompt(
            id=entry["id"],
            guid=guid,
            name=entry["name"],
            description=entry["description"],
            artifact_path=dest_filename,
            tags=entry["tags"]
        )
        db_session.add(prompt)
        print(f"Seeded AgentPrompt '{entry['name']}' with ID: {entry['id']} and GUID: {guid}")

    for entry in SYSTEM_PROMPT_FILES:
        guid = str(uuid4())
        dest_filename = f"{guid}.txt"
        content = fm.load(FILETYPE.SEED_SOURCE, entry["filename"])
        fm.save(FILETYPE.EXTENSION, dest_filename, content)

        prompt = SystemPrompt(
            id=entry["id"],
            guid=guid,
            name=entry["name"],
            system_type=entry["system_type"],
            description=entry["description"],
            artifact_path=dest_filename,
            tags=entry["tags"]
        )
        db_session.add(prompt)
        print(f"Seeded SystemPrompt '{entry['name']}' with ID: {entry['id']} and GUID: {guid}")

    db_session.commit()
