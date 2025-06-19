from uuid import uuid4
from pathlib import Path
import shutil
from sqlalchemy.orm import Session
from app.db.models import ToolProviderConfig
from app.enums.logging_enums import PROVIDER_TYPE

CURRENT_DIR = Path(__file__).resolve().parent
SEED_FILES_DIR = CURRENT_DIR / "files/tool_providers"
PROJECT_ROOT = SEED_FILES_DIR.parent.parent.parent.parent.parent
EXTENSIONS_DIR = PROJECT_ROOT / "extensions"

TOOLS = [
    {
        "id": 1,
        "filename": "black_tool.py",
        "name": "black",
        "description": "Formats Python code using Black.",
        "config": {"components": {}, "params": {}}
    },
    {
        "id": 2,
        "filename": "sonarcloud_tool.py",
        "name": "sonarcloud",
        "description": "Static analysis via SonarCloud.",
        "config": {"components": {}, "params": {}}
    },
    {
        "id": 3,
        "filename": "ruff_tool.py",
        "name": "ruff",
        "description": "Python linting with Ruff.",
        "config": {"components": {}, "params": {}}
    },
    {
        "id": 4,
        "filename": "radon_tool.py",
        "name": "radon",
        "description": "Analyzes Python code complexity.",
        "config": {"components": {}, "params": {}}
    },
    {
        "id": 5,
        "filename": "mypy_tool.py",
        "name": "mypy",
        "description": "Static type checking with mypy.",
        "config": {"components": {}, "params": {}}
    },
    {
        "id": 6,
        "filename": "docformatter_tool.py",
        "name": "docformatter",
        "description": "Formats docstrings using docformatter.",
        "config": {"components": {}, "params": {}}
    },
    {
        "id": 7,
        "filename": "symbol_graph.py",
        "name": "symbol_graph",
        "description": "Extracts and analyzes Python symbols into structured graphs.",
        "config": {"components": {}, "params": {}}
    }
]

def seed_tool_providers(db_session: Session):
    EXTENSIONS_DIR.mkdir(parents=True, exist_ok=True)

    for entry in TOOLS:
        guid = str(uuid4())
        dest_filename = f"{guid}.py"
        source_file = SEED_FILES_DIR / entry["filename"]
        dest_file = EXTENSIONS_DIR / dest_filename

        if not source_file.exists():
            raise FileNotFoundError(f"Tool script not found: {source_file}")

        shutil.copy(source_file, dest_file)

        tool = ToolProviderConfig(
            id=entry["id"],
            guid=guid,
            name=entry["name"],
            description=entry["description"],
            config=entry["config"],
            artifact_path=dest_filename,
            provider_type=PROVIDER_TYPE.TOOL,
        )

        db_session.add(tool)

    db_session.commit()
    print("Seeded tool configurations successfully.")
