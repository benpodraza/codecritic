from uuid import uuid4
from sqlalchemy.orm import Session

from app.db.models import ToolProviderConfig
from app.enums.logging_enums import PROVIDER_TYPE
from app.utilities.file_management.file_utils import get_file_manager, FILETYPE

fm = get_file_manager()

TOOLS = [
    {
        "id": 1,
        "filename": "tool_providers/black_tool.py",
        "name": "black",
        "description": "Formats Python code using Black.",
        "config": {"components": {}, "params": {}}
    },
    {
        "id": 2,
        "filename": "tool_providers/sonarcloud_tool.py",
        "name": "sonarcloud",
        "description": "Static analysis via SonarCloud.",
        "config": {"components": {}, "params": {}}
    },
    {
        "id": 3,
        "filename": "tool_providers/ruff_tool.py",
        "name": "ruff",
        "description": "Python linting with Ruff.",
        "config": {"components": {}, "params": {}}
    },
    {
        "id": 4,
        "filename": "tool_providers/radon_tool.py",
        "name": "radon",
        "description": "Analyzes Python code complexity.",
        "config": {"components": {}, "params": {}}
    },
    {
        "id": 5,
        "filename": "tool_providers/mypy_tool.py",
        "name": "mypy",
        "description": "Static type checking with mypy.",
        "config": {"components": {}, "params": {}}
    },
    {
        "id": 6,
        "filename": "tool_providers/docformatter_tool.py",
        "name": "docformatter",
        "description": "Formats docstrings using docformatter.",
        "config": {"components": {}, "params": {}}
    },
    {
        "id": 7,
        "filename": "tool_providers/symbol_graph.py",
        "name": "symbol_graph",
        "description": "Extracts and analyzes Python symbols into structured graphs.",
        "config": {"components": {}, "params": {}}
    }
]

def seed_tool_providers(db_session: Session):
    for entry in TOOLS:
        guid = str(uuid4())
        dest_filename = f"{guid}.py"
        content = fm.load(FILETYPE.SEED_SOURCE, entry["filename"])
        fm.save(FILETYPE.EXTENSION, dest_filename, content)

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
    print("✅ Seeded tool configurations successfully.")
