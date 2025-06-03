from __future__ import annotations
from pathlib import Path
import textwrap
import json

from app.providers.prompt_provider_base import PromptProviderBase
from app.db.schemas import PromptOutputSchema

class LintingPromptProvider(PromptProviderBase):
    def _run(self, input: dict) -> PromptOutputSchema:
        session_id = input.get("session_id")
        system = input.get("system", "unknown")
        file_path = input.get("file_path")

        if not session_id or not file_path:
            raise ValueError("PromptProvider requires both session_id and file_path")

        if not self.agent_text or not self.system_text or not self._context_provider:
            raise ValueError("Missing required prompt text or context provider")

        context_output = self._context_provider.run({
            "file_path": file_path,
            "session_id": session_id,
            "system": system
        })
        context = context_output.context if hasattr(context_output, "context") else json.loads(context_output)

        convo_section = "\n".join(context.get("conversation_log", [])) or "(none)"
        score = context.get("score", {}).get("value", "unknown")
        source_code = context.get("source_code", "")

        full_prompt = textwrap.dedent(f"""\

            {self.agent_text}

            ---

            {self.system_text}

            ---

            Score: {score}
            Conversation Log:
            {convo_section}

            ---

            [SOURCE_CODE]
            {source_code.rstrip()}
            [/SOURCE_CODE]
        """)

        return PromptOutputSchema(
            prompt=full_prompt,
            summary=f"Prompt for file: {Path(file_path).name} with score {score}"
        )
