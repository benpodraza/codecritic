from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from pathlib import Path
from app.db.seeders.seed_controller_providers import seed_controller_providers
from app.db.seeders.seed_program_provider import seed_program_providers
from app.db.seeders.seed_state_providers import seed_state_providers
from app.db.seeders.seed_agent_engine_providers import seed_agent_engine_providers
from app.db.seeders.seed_context_providers import seed_context_providers
from app.db.seeders.seed_prompt_providers import seed_prompt_providers
from app.db.seeders.seed_score_providers import seed_score_providers
from app.db.seeders.seed_system_providers import seed_system_providers
from app.db.seeders.seed_tool_providers import seed_tool_providers
from app.db.seeders.seed_prompts import seed_prompts

# Ensure your project root matches explicitly
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "experiments" / "codecritic.sqlite3"
EXTENSIONS_DIR = PROJECT_ROOT / "extensions"

def main():
    engine = create_engine(f"sqlite:///{DB_PATH}")
    with Session(bind=engine) as session:
        seed_prompts(session)
        seed_prompt_providers(session)
        seed_tool_providers(session)
        seed_score_providers(session)
        seed_context_providers(session)
        seed_agent_engine_providers(session)
        seed_state_providers(session)
        seed_system_providers(session)
        seed_controller_providers(session)
        seed_program_providers(session)

    print(f"Database seeded successfully at {DB_PATH.resolve()}")

if __name__ == "__main__":
    main()
