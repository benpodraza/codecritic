from app.providers.agent_provider_base import AgentProviderBase
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.db.connection import DB_PATH
from app.db.models import (
    PromptProviderConfig,
    AgentEngineProviderConfig,
    AgentPrompt,
    SystemPrompt
)
from app.factories.prompt_provider_factory import PromptProviderFactory
from app.factories.agent_engine_provider_factory import AgentEngineProviderFactory

class LintingGeneratorAgentProvider(AgentProviderBase):
    """Runs a GPT-4o generation round using the linting system prompt, context, and snapshot."""

    def _run(self, input: dict) -> str:
        session_id = self._session_id
        file_path = input["file_path"]
        context = input["context"]

        # 🔌 Local engine
        engine = create_engine(f"sqlite:///{DB_PATH}")

        # 📦 Load config objects from DB
        with Session(bind=engine) as session:
            prompt_row = session.query(PromptProviderConfig).filter_by(name="linting_prompt_provider").first()
            engine_row = session.query(AgentEngineProviderConfig).filter_by(name="openai_gpt_4o_agent_engine").first()
            agent_prompt = session.query(AgentPrompt).filter_by(name="linting_generator_agent").first()
            system_prompt = session.query(SystemPrompt).filter_by(name="linting_system").first()

        # 🧠 Build prompt
        prompt_provider = PromptProviderFactory.create(prompt_row.id)
        final_prompt = prompt_provider.run(
            input={
                "agent_prompt_path": agent_prompt.artifact_path,
                "system_prompt_path": system_prompt.artifact_path,
                "context": context
            },
            session_id=session_id
        )

        # 🤖 Run LLM engine
        engine_provider = AgentEngineProviderFactory.create(
            engine_row.id,
            config_override={"before": str(Path(file_path).resolve())}
        )

        return engine_provider.run(
            input={"prompt": final_prompt, "before": str(file_path)},
            session_id=session_id
        )
