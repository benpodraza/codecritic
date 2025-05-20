from pathlib import Path
import shutil
from sqlalchemy.orm import Session
from uuid import uuid4
from app.db.models import AgentPrompt, SystemPrompt

# Define paths relative to this script's file location explicitly
CURRENT_DIR = Path(__file__).resolve().parent
SEED_FILES_DIR = CURRENT_DIR / "files"
PROJECT_ROOT = CURRENT_DIR.parent.parent.parent  # adjust based on your actual folder structure
EXTENSIONS_DIR = PROJECT_ROOT / "extensions"

def seed_prompts(db_session: Session):
    # Ensure extensions directory exists explicitly
    EXTENSIONS_DIR.mkdir(parents=True, exist_ok=True)

    # Seed AgentPrompt
    agent_guid = str(uuid4())
    agent_source_file = SEED_FILES_DIR / "basic_agent_prompt.txt"
    agent_dest_file = EXTENSIONS_DIR / f"{agent_guid}.txt"

    # Explicit check for source file existence
    if not agent_source_file.exists():
        raise FileNotFoundError(f"Agent source file not found: {agent_source_file}")

    shutil.copy(agent_source_file, agent_dest_file)

    agent_prompt = AgentPrompt(
        guid=agent_guid,
        name="generate",
        description="Prompt for basic code generation.",
        artifact_path=str(agent_dest_file),
        tags=["linting", "generation"]
    )

    # Seed SystemPrompt
    system_guid = str(uuid4())
    system_source_file = SEED_FILES_DIR / "default_system_prompt.txt"
    system_dest_file = EXTENSIONS_DIR / f"{system_guid}.txt"

    # Explicit check for system source file existence
    if not system_source_file.exists():
        raise FileNotFoundError(f"System source file not found: {system_source_file}")

    shutil.copy(system_source_file, system_dest_file)

    system_prompt = SystemPrompt(
        guid=system_guid,
        name="format",
        description="Default prompt for formatting tasks.",
        artifact_path=str(system_dest_file),
        tags=["formatting", "default"]
    )

    # Insert into database
    db_session.add(agent_prompt)
    db_session.add(system_prompt)
    db_session.commit()

    print(f"Seeded AgentPrompt GUID: {agent_guid}")
    print(f"Seeded SystemPrompt GUID: {system_guid}")
