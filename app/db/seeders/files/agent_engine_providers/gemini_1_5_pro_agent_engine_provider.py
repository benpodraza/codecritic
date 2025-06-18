import os
import requests

from app.enums.logging_enums import RunContext
from app.db.schemas import AgentEngineOutput
from app.providers.agent_engine_provider_base import AgentEngineProviderBase


class Gemini1_5ProAgentEngineProvider(AgentEngineProviderBase):
    def _run(self, input: dict, context: RunContext | None = None) -> AgentEngineOutput:
        if not self.prompt_provider:
            raise ValueError("Prompt provider is required to extract engine output.")

        # Step 1: Run prompt provider to generate prompt
        prompt_output = self.prompt_provider.run(input=input, context=context)
        prompt = prompt_output.prompt

        # Step 2: Call Gemini API with prompt
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
        raw_response = response_raw.json()["candidates"][0]["content"]["parts"][0]["text"].strip()

        # Step 3: Extract structured response using prompt provider
        extracted = self.prompt_provider._extract(raw_response)

        # Step 4: Build engine output
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
