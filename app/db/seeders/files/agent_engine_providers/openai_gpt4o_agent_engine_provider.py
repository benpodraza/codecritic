import os

from app.db.schemas import AgentEngineOutput
from app.enums.fsm_enums import DECISION_TYPE
from app.enums.logging_enums import RunContext
from app.providers.agent_engine_provider_base import AgentEngineProviderBase


class OpenAIGPT4oAgentEngineProvider(AgentEngineProviderBase):
    def _run(
        self,
        input: dict,
        context: RunContext | None = None,
        prompt_provider=None
    ) -> AgentEngineOutput:
        input = dict(input)

        if not prompt_provider:
            raise ValueError("Missing prompt_provider argument")

        try:
            prompt_output = prompt_provider.run(input=input, context=context)
            if not prompt_output or not getattr(prompt_output, "prompt", None):
                raise RuntimeError("prompt_provider.run() returned invalid output.")
            prompt = prompt_output.prompt
        except Exception as e:
            raise

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise EnvironmentError("OPENAI_API_KEY is not set in the environment.")

        temperature = float(input.get("temperature", 0.2))
        max_tokens = int(input.get("max_tokens", 2048))

        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            raw_response = response.choices[0].message.content.strip()
        except Exception as e:
            raise

        try:
            extracted = prompt_provider._extract(raw_response)
        except Exception as e:
            raise

        token_count = len(raw_response.split()) if raw_response else 0
        cost_usd = token_count * (self._config.cost_per_1k_tokens or 0.0) / 1000

        return AgentEngineOutput(
            response=raw_response,
            token_count=token_count,
            cost_usd=cost_usd,
            content=extracted.content,
            decision=DECISION_TYPE.UNKNOWN,
            log=extracted.log
        )
