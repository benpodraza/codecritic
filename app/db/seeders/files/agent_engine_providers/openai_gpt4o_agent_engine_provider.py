import json
import os
from openai import OpenAI
from app.db.schemas import AgentEngineOutput
from app.providers.agent_engine_provider_base import AgentEngineProviderBase

def _safe_prompt_content(content):
    if isinstance(content, str):
        return content
    if hasattr(content, "model_dump_json"):
        return content.model_dump_json()
    if isinstance(content, dict):
        return json.dumps(content)
    return str(content)

class OpenAIGPT4oAgentEngineProvider(AgentEngineProviderBase):
    def _run(self, input: dict) -> AgentEngineOutput:
        prompt = input["prompt"]
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise EnvironmentError("OPENAI_API_KEY is not set in the environment.")

        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": _safe_prompt_content(prompt)},
            ],
            temperature=0.2,
            max_tokens=2048,
        )

        content = response.choices[0].message.content.strip()
        token_count = len(content.split())
        cost_usd = token_count * (self._config.cost_per_1k_tokens or 0.0) / 1000

        return AgentEngineOutput(response=content, token_count=token_count, cost_usd=cost_usd)
