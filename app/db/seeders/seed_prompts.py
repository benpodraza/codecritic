from pathlib import Path
import shutil
from sqlalchemy.orm import Session
from uuid import uuid4
from app.db.models import AgentPrompt, SystemPrompt
from app.enums.system_enums import SYSTEM_TYPE

# Define paths relative to this script's file location explicitly
CURRENT_DIR = Path(__file__).resolve().parent
SEED_FILES_DIR = CURRENT_DIR / "files/prompts"
PROJECT_ROOT = CURRENT_DIR.parent.parent.parent
EXTENSIONS_DIR = PROJECT_ROOT / "extensions"

# Define new prompt files to seed
AGENT_PROMPT_FILES = [
    {
        "id": 1,
        "name": "generate",
        "filename": "basic_agent_prompt.txt",
        "description": "Prompt for basic code generation.",
        "tags": ["linting", "generator"]
    },
    {
        "id": 2,
        "name": "linting_generator_agent",
        "filename": "linting_generator_agent_prompt.txt",
        "description": "Prompt for linting generator agent.",
        "tags": ["linting", "generator"]
    }
]

SYSTEM_PROMPT_FILES = [
    {
        "id": 1,
        "name": "format",
        "filename": "default_system_prompt.txt",
        "system_type": SYSTEM_TYPE.LINTING,
        "description": "Default prompt for formatting tasks.",
        "tags": ["formatting", "default"]
    },
    {
        "id": 2,
        "name": "linting_system",
        "filename": "linting_system_prompt.txt",
        "system_type": SYSTEM_TYPE.LINTING,
        "description": "System prompt governing the linting subsystem.",
        "tags": ["linting", "system"]
    }
]


def seed_prompts(db_session: Session):
    EXTENSIONS_DIR.mkdir(parents=True, exist_ok=True)

    for entry in AGENT_PROMPT_FILES:
        source_file = SEED_FILES_DIR / entry["filename"]
        if not source_file.exists():
            raise FileNotFoundError(f"Agent prompt source file not found: {source_file}")

        guid = str(uuid4())
        dest_filename = f"{guid}.txt"
        dest_file = EXTENSIONS_DIR / dest_filename
        shutil.copy(source_file, dest_file)

        prompt = AgentPrompt(
            id=entry["id"],
            guid=guid,
            name=entry["name"],
            description=entry["description"],
            artifact_path=dest_filename,  # Store relative path
            tags=entry["tags"]
        )
        db_session.add(prompt)
        print(f"Seeded AgentPrompt '{entry['name']}' with ID: {entry['id']} and GUID: {guid}")

    for entry in SYSTEM_PROMPT_FILES:
        source_file = SEED_FILES_DIR / entry["filename"]
        if not source_file.exists():
            raise FileNotFoundError(f"System prompt source file not found: {source_file}")

        guid = str(uuid4())
        dest_filename = f"{guid}.txt"
        dest_file = EXTENSIONS_DIR / dest_filename
        shutil.copy(source_file, dest_file)

        prompt = SystemPrompt(
            id=entry["id"],
            guid=guid,
            name=entry["name"],
            system_type=entry["system_type"],
            description=entry["description"],
            artifact_path=dest_filename,  # Store relative path
            tags=entry["tags"]
        )
        db_session.add(prompt)
        print(f"Seeded SystemPrompt '{entry['name']}' with ID: {entry['id']} and GUID: {guid}")

    db_session.commit()