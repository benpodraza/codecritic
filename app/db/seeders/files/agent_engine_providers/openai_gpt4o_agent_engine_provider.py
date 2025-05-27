import os
from openai import OpenAI
from app.providers.agent_engine_provider_base import AgentEngineProviderBase

class OpenAIGPT4oAgentEngineProvider(AgentEngineProviderBase):
    def _run(self, input: dict) -> str:
        prompt = input["prompt"]
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise EnvironmentError("OPENAI_API_KEY is not set in the environment.")

        client = OpenAI(api_key=api_key)

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a high-precision agent executing structured code refinement tasks."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=2048,
        )

        return response.choices[0].message.content.strip()
