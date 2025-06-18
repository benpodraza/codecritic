from app.db.schemas import AgentEngineOutput
from app.enums.fsm_enums import DECISION_TYPE
from app.providers.agent_engine_provider_base import AgentEngineProviderBase
from app.enums.logging_enums import RunContext
from openai import OpenAI
import os

class OpenAIGPT4oAgentEngineProvider(AgentEngineProviderBase):
    def _run(self, input: dict, context: RunContext | None = None) -> AgentEngineOutput:
        prompt_provider = input.get("prompt_provider") 
        input = {k: v for k, v in input.items() if k != "prompt_provider"}

        if not prompt_provider:
            raise ValueError("Prompt provider is required to extract engine output.")

        try:
            prompt_output = prompt_provider.run(input=input, context=context)
            if prompt_output is None:
                raise RuntimeError("❌ prompt_provider.run() returned None")
            prompt = prompt_output.prompt
        except Exception as e:
            print("❌ Error during prompt generation:")
            print(e)
            raise

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise EnvironmentError("OPENAI_API_KEY is not set in the environment.")

        try:
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
                max_tokens=2048,
            )
            raw_response = response.choices[0].message.content.strip()
        except Exception as e:
            print("❌ Error during OpenAI API call:")
            print(e)
            raise

        try:
            extracted = prompt_provider._extract(raw_response)
        except Exception as e:
            print("❌ Error during response extraction:")
            print(e)
            print(f"🔍 Raw response was:\n{raw_response}")
            raise

        token_count = len(raw_response.split())
        cost_usd = token_count * (self._config.cost_per_1k_tokens or 0.0) / 1000

        return AgentEngineOutput(
            response=raw_response,
            token_count=token_count,
            cost_usd=cost_usd,
            content=extracted.content,
            decision=DECISION_TYPE.UNKNOWN,
            log=extracted.log
        )
