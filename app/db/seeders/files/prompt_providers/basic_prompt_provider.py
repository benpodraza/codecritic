from app.providers.prompt_provider_base import PromptProviderBase
from app.db.schemas import PromptOutputSchema

class BasicPromptProvider(PromptProviderBase):
    def _run(self, input: dict) -> PromptOutputSchema:
        agent_config = input.get("agent_config", {})
        system_config = input.get("system_config", {})

        prompt = (
            f"User: {agent_config.get('input', 'No input provided')}\n"
            f"System: Response mode: {system_config.get('setting', 'default')}"
        )

        return PromptOutputSchema(
            prompt=prompt,
            summary="Basic prompt using agent and system config"
        )
