from app.providers.prompt_provider_base import PromptProviderBase

class BasicPromptProvider(PromptProviderBase):
    def _run(self, input: dict) -> str:
        agent_config = input.get("agent_config", {})
        system_config = input.get("system_config", {})

        return f"User: {agent_config.get('input', 'No input provided')}\nSystem: Response mode: {system_config.get('setting', 'default')}"
