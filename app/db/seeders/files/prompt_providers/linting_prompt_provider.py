from __future__ import annotations
import json
from pathlib import Path

from app.enums.logging_enums import RunContext
from app.providers.prompt_provider_base import PromptProviderBase
from app.db.schemas import AgentEngineExtraction, PromptOutputSchema
from app.utilities.extract_code_block import extract_code_blocks


class LintingPromptProvider(PromptProviderBase):
    def _run(self, input: dict, context: RunContext | None = None) -> PromptOutputSchema:
        session_id = self._session_id
        system = input.get("system", "unknown")
        file_path = input.get("file_path")

        if not self.agent_text or not self.system_text or not self._context_provider:
            raise ValueError("Missing required prompt text or context provider")

        # ✅ propagate context to context provider
        context_output = self._context_provider.run(
            {
                "file_path": file_path,
                "system": system
            },
            context=context
        )

        context = (
            context_output.context
            if hasattr(context_output, "context")
            else json.loads(context_output)
        )

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

        # 🧾 Construct summary based on the file path and system
        short_path = Path(file_path).name if file_path else "unknown file"
        summary = f"Linting prompt generated for {short_path} (system: {system})"

        return PromptOutputSchema(prompt=full_prompt, summary=summary)

    def _extract(self, response: str) -> AgentEngineExtraction:
        return extract_code_blocks(response)