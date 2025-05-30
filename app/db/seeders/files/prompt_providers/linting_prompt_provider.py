from __future__ import annotations
from pathlib import Path
from app.providers.prompt_provider_base import PromptProviderBase
import textwrap
import json

class LintingPromptProvider(PromptProviderBase):
    def __init__(self, config, engine=None):
        super().__init__(config=config, engine=engine)

        EXTENSIONS_DIR = Path(__file__).resolve().parent

        if not self._agent_prompt:
            raise ValueError("PromptProvider is missing required AgentPrompt")
        if not self._system_prompt:
            raise ValueError("PromptProvider is missing required SystemPrompt")
        if not self._context_provider:
            raise ValueError("PromptProvider is missing required ContextProvider")

        self.agent_prompt_path = (EXTENSIONS_DIR / self._agent_prompt.artifact_path).resolve()
        self.system_prompt_path = (EXTENSIONS_DIR / self._system_prompt.artifact_path).resolve()

    def _run(self, input: dict) -> str:
        session_id = input.get("session_id")
        system = input.get("system", "unknown")
        file_path = input.get("file_path")

        if not session_id or not file_path:
            raise ValueError("PromptProvider requires both session_id and file_path")

        if not self.agent_prompt_path.exists():
            raise FileNotFoundError(f"Agent prompt not found: {self.agent_prompt_path}")
        if not self.system_prompt_path.exists():
            raise FileNotFoundError(f"System prompt not found: {self.system_prompt_path}")

        # 🎯 Build context using the injected context provider
        raw_context = self._context_provider.run(
            {
                "file_path": file_path,
                "session_id": session_id,
                "system": system
            }
        )
        context = json.loads(raw_context)

        agent_text = self.agent_prompt_path.read_text(encoding="utf-8").strip()
        system_text = self.system_prompt_path.read_text(encoding="utf-8").strip()
        convo_section = "\n".join(context.get("conversation_log", [])) or "(none)"
        score = context.get("score", {}).get("value", "unknown")
        source_code = context.get("source_code", "")

        return textwrap.dedent(f"""\

            {agent_text}

            ---

            {system_text}

            ---

            Score: {score}
            Conversation Log:
            {convo_section}

            ---

            [SOURCE_CODE]
            {source_code.rstrip()}
            [/SOURCE_CODE]
        """)
