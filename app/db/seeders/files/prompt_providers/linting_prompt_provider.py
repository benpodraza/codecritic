from __future__ import annotations
from pathlib import Path
from app.providers.prompt_provider_base import PromptProviderBase
import textwrap

class LintingPromptProvider(PromptProviderBase):
    def _run(self, input: dict) -> str:
        context = input.get("context", {})
        score = context.get("score", {}).get("value", "unknown")
        convo_log = context.get("conversation_log", [])
        source_code = context.get("source_code", "")

        agent_prompt_path = Path(input.get("agent_prompt_path", "")).resolve()
        system_prompt_path = Path(input.get("system_prompt_path", "")).resolve()

        if not agent_prompt_path.exists():
            raise FileNotFoundError(f"Agent prompt not found: {agent_prompt_path}")
        if not system_prompt_path.exists():
            raise FileNotFoundError(f"System prompt not found: {system_prompt_path}")

        agent_text = agent_prompt_path.read_text(encoding="utf-8").strip()
        system_text = system_prompt_path.read_text(encoding="utf-8").strip()

        convo_section = "\n".join(convo_log) if convo_log else "(none)"

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
