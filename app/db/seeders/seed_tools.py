from uuid import uuid4
from pathlib import Path
import shutil
from sqlalchemy.orm import Session

from app.db.models import ToolProviderConfig


CURRENT_DIR = Path(__file__).resolve().parent
SEED_FILES_DIR = CURRENT_DIR / "files/tool_providers"
PROJECT_ROOT = SEED_FILES_DIR.parent.parent.parent.parent.parent
EXTENSIONS_DIR = PROJECT_ROOT / "extensions"

TOOLS = [
    ("black_tool.py", "Black Formatter", "Formats Python code using Black.", {}),
    ("sonarcloud_tool.py", "SonarCloud Analyzer", "Static analysis via SonarCloud.", {}),
    ("ruff_tool.py", "Ruff Linter", "Python linting with Ruff.", {}),
    ("radon_tool.py", "Radon Analyzer", "Analyzes Python code complexity.", {}),
    ("mypy_tool.py", "Mypy Type Checker", "Static type checking with mypy.", {}),
    ("docformatter_tool.py", "Docformatter Formatter", "Static type checking with mypy.", {}),
    ("symbol_graph.py", "Symbol Graph Analyzer", "Extracts and analyzes Python symbols into structured graphs.", {}),
]

def seed_tool_providers(db_session: Session):
    EXTENSIONS_DIR.mkdir(parents=True, exist_ok=True)

    for filename, name, description, config in TOOLS:
        guid = str(uuid4())
        source_file = SEED_FILES_DIR / filename
        dest_file = EXTENSIONS_DIR / f"{guid}.py"

        if not source_file.exists():
            raise FileNotFoundError(f"Tool script not found: {source_file}")

        shutil.copy(source_file, dest_file)

        tool = ToolProviderConfig(
            guid=guid,
            name=name,
            description=description,
            config=config,
            artifact_path=guid
        )

        db_session.add(tool)

    db_session.commit()
    print("Seeded tool configurations successfully.")
