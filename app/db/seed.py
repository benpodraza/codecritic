from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from pathlib import Path
from app.db.seeders.seed_tools import seed_tools
from app.db.seeders.seed_prompts import seed_prompts

# Ensure your project root matches explicitly
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "experiments" / "codecritic.sqlite3"
EXTENSIONS_DIR = PROJECT_ROOT / "extensions"

def main():
    engine = create_engine(f"sqlite:///{DB_PATH}")
    with Session(bind=engine) as session:
        seed_prompts(session)
        seed_tools(session)
    print(f"Database seeded successfully at {DB_PATH.resolve()}")

if __name__ == "__main__":
    main()
