import os, requests
from app.db.schemas import AgentEngineOutput
from app.providers.agent_engine_provider_base import AgentEngineProviderBase

class Gemini1_5ProAgentEngineProvider(AgentEngineProviderBase):
    def _run(self, input: dict) -> AgentEngineOutput:
        prompt = input["prompt"]
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise EnvironmentError("GOOGLE_API_KEY is not set in the environment.")

        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent"
            f"?key={api_key}"
        )
        response_raw = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            json={"contents": [{"parts": [{"text": prompt}]}]},
        )
        response_raw.raise_for_status()
        content = response_raw.json()["candidates"][0]["content"]["parts"][0]["text"].strip()

        token_count = len(content.split())
        cost_usd = token_count * (self._config.cost_per_1k_tokens or 0.0) / 1000

        return AgentEngineOutput(response=content, token_count=token_count, cost_usd=cost_usd)
