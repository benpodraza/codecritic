from __future__ import annotations

import json
from pathlib import Path

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

        context_output = self._context_provider.run(
            {
                "file_path": file_path,
                "system": system
            },
            session_id=session_id
        )
        context = context_output.context if hasattr(context_output, "context") else json.loads(context_output)

        convo_section = "\n".join(context.get("conversation_log", [])) or "(none)"

        full_prompt = f"""
{self.system_text}

---

{self.agent_text}

---

[CONTEXT]
{json.dumps(context, indent=2)}

---

[CONVERSATION LOG]
{convo_section}
""".strip()

        return PromptOutputSchema(prompt=full_prompt)
