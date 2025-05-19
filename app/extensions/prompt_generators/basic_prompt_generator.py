from __future__ import annotations

from typing import Any, Dict

from ...abstract_classes.prompt_generator_base import PromptGeneratorBase
from ...abstract_classes.context_provider_base import ContextProviderBase
from ...factories.logging_provider import LoggingProvider


class BasicPromptGenerator(PromptGeneratorBase):
    """Combine system and agent templates with code context."""

    def __init__(
        self,
        context_provider: ContextProviderBase,
        logger: LoggingProvider | None = None,
    ) -> None:
        super().__init__(logger)
        self.context_provider = context_provider

    def _generate_prompt(
        self, agent_config: Dict[str, Any], system_config: Dict[str, Any]
    ) -> str:
        context = self.context_provider.get_context()
        self._log.debug("Raw context: %s", context)

        system_template = system_config.get("template", "")
        agent_template = agent_config.get("template", "")

        context_snippet = ""
        if context:
            funcs = ", ".join(context.get("functions", []))
            classes = ", ".join(context.get("classes", {}).keys())
            context_snippet = f"Functions: {funcs}\nClasses: {classes}"

        prompt = f"{agent_template}\n\n{system_template}\n\n{context_snippet}"
        self._log.info("Prompt generated")
        self._log.debug("Prompt content: %s", prompt)
        return prompt
