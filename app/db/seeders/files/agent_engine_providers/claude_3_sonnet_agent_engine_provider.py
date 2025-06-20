import os
import json
import boto3

from app.enums.logging_enums import RunContext
from app.db.schemas import AgentEngineOutput
from app.providers.agent_engine_provider_base import AgentEngineProviderBase


class Claude3SonnetAgentEngineProvider(AgentEngineProviderBase):
    def _run(self, input: dict, context: RunContext | None = None) -> AgentEngineOutput:
        if not self.prompt_provider:
            raise ValueError("Prompt provider is required to extract engine output.")

        # Step 1: Generate prompt
        prompt_output = self.prompt_provider.run(input=input, context=context)
        prompt = getattr(prompt_output, "prompt", None)
        if not prompt:
            raise RuntimeError("Prompt provider returned invalid output or missing prompt.")

        # Step 2: Configurable parameters
        max_tokens = int(input.get("max_tokens", 1024))
        temperature = float(input.get("temperature", 0.2))

        # Step 3: Call Claude via AWS Bedrock
        region = os.getenv("AWS_REGION", "us-east-1")
        client = boto3.client("bedrock-runtime", region_name=region)

        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        try:
            response_raw = client.invoke_model(
                modelId="anthropic.claude-3-sonnet-20240229-v1:0",
                contentType="application/json",
                accept="application/json",
                body=json.dumps(body),
            )
            response_data = json.loads(response_raw["body"].read())
            raw_response = response_data["content"][0]["text"].strip()
        except Exception as e:
            raise RuntimeError(f"❌ Claude API call failed or returned unexpected structure: {e}")

        token_count = len(raw_response.split()) if raw_response else 0
        cost_usd = token_count * (self._config.cost_per_1k_tokens or 0.0) / 1000

        # Step 4: Parse
        extracted = self.prompt_provider._extract(raw_response)

        return AgentEngineOutput(
            response=raw_response,
            token_count=token_count,
            cost_usd=cost_usd,
            content=extracted.content,
            decision=extracted.decision,
            log=extracted.log
        )
