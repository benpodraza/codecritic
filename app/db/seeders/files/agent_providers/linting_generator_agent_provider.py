from app.providers.agent_provider_base import AgentProviderBase
import textwrap

class LintingGeneratorAgentProvider(AgentProviderBase):
    """Runs a GPT-4o generation round using the linting system prompt, context, and snapshot."""

    def __init__(self, config=None, engine=None, **kwargs):
        super().__init__(config=config, engine=engine, **kwargs)

    def _run(self, input: dict) -> str:
        session_id = self._session_id
        file_path = input["file_path"]
        system = input.get("system", "linting")

        if not self._prompt_provider:
            raise ValueError("Prompt provider is not set")
        if not self._agent_engine:
            raise ValueError("Agent engine is not set")

        # 🧠 Build final prompt
        final_prompt = self._prompt_provider.run(
            input=input,  # pass through exactly what was received
            session_id=session_id
        )

        # 🤖 Run LLM engine
        return self._agent_engine.run(
            input={
                "prompt": final_prompt,
                "before": file_path
            },
            session_id=session_id
        )
