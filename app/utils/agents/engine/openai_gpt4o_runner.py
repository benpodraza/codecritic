import os
import re
from typing import Any
from openai import OpenAI
from app.utils.agents.engine.agent_engine_runner import AgentEngineRunner

# === ENV + CLIENT ===
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise EnvironmentError("❌ OPENAI_API_KEY is not set in the environment.")

client = OpenAI(api_key=OPENAI_API_KEY)

# === HELPERS ===
def extract_python_code(response: str) -> str:
    match = re.search(r"```python(.*?)```", response, re.DOTALL)
    return match.group(1).strip() if match else response.strip()

class OpenAiGpt4oAgentEngineRunner(AgentEngineRunner):
    def call_engine(self, prompt: str, config: dict[str, Any]) -> str:
        model = config.get("model", "gpt-4o")
        system_prompt = config.get("system_role", "You are an expert Python code refactoring agent.")
        temperature = config.get("temperature", 0.3)

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature
        )
        return extract_python_code(response.choices[0].message.content)