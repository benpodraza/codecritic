import os
import requests

from app.enums.logging_enums import RunContext
from app.db.schemas import AgentEngineOutput
from app.providers.agent_engine_provider_base import AgentEngineProviderBase


class Gemini1_5ProAgentEngineProvider(AgentEngineProviderBase):
    def _run(self, input: dict, context: RunContext | None = None) -> AgentEngineOutput:
        if not self.prompt_provider:
            raise ValueError("Prompt provider is required to extract engine output.")

        prompt_output = self.prompt_provider.run(input=input, context=context)
        prompt = prompt_output.prompt

        api_key = os.getenv("GOOGLE_API_KEY")
        uri = os.getenv("GOOGLE_URI")
        if not api_key:
            raise EnvironmentError("GOOGLE_API_KEY is not set in the environment.")
        if not uri:
            raise EnvironmentError("GOOGLE_URI is not set in the environment.")

        temperature = float(input.get("temperature", 0.2))
        max_tokens = int(input.get("max_tokens", 2048))

        url = f"{uri}?key={api_key}"
        response_raw = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": temperature,
                    "maxOutputTokens": max_tokens
                }
            },
        )
        response_raw.raise_for_status()

        try:
            raw_response = response_raw.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
        except (KeyError, IndexError, TypeError) as e:
            raise RuntimeError(f"❌ Gemini response structure unexpected: {e}")

        extracted = self.prompt_provider._extract(raw_response)

        token_count = len(raw_response.split())
        cost_usd = token_count * (self._config.cost_per_1k_tokens or 0.0) / 1000

        return AgentEngineOutput(
            response=raw_response,
            token_count=token_count,
            cost_usd=cost_usd,
            content=extracted.content,
            decision=extracted.decision,
            log=extracted.log
        )
