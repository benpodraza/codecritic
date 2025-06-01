# extensions/gemini_1_5_pro_agent_engine_provider.py
import os
import requests
from app.providers.agent_engine_provider_base import AgentEngineProviderBase


class Gemini1_5ProAgentEngineProvider(AgentEngineProviderBase):
    def _run(self, input: dict) -> str:
        prompt = input["prompt"]
        api_key = os.getenv("GOOGLE_API_KEY")

        if not api_key:
            raise EnvironmentError("GOOGLE_API_KEY is not set in the environment.")

        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent"
            f"?key={api_key}"
        )

        response = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            json={"contents": [{"parts": [{"text": prompt}]}]}
        )

        response.raise_for_status()
        result = response.json()

        return result["candidates"][0]["content"]["parts"][0]["text"].strip()