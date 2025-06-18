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

        # Step 1: Generate prompt using prompt provider
        prompt_output = self.prompt_provider.run(input=input, context=context)
        prompt = prompt_output.prompt

        # Step 2: Call Claude via Bedrock
        region = os.getenv("AWS_REGION", "us-east-1")
        client = boto3.client("bedrock-runtime", region_name=region)
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1024,
        }

        response_raw = client.invoke_model(
            modelId="anthropic.claude-3-sonnet-20240229-v1:0",
            contentType="application/json",
            accept="application/json",
            body=json.dumps(body),
        )

        raw_response = json.loads(response_raw["body"].read())["content"][0]["text"].strip()
        token_count = len(raw_response.split())
        cost_usd = token_count * (self._config.cost_per_1k_tokens or 0.0) / 1000

        # Step 3: Extract structured response using prompt provider
        extracted = self.prompt_provider._extract(raw_response)

        return AgentEngineOutput(
            response=raw_response,
            token_count=token_count,
            cost_usd=cost_usd,
            content=extracted.content,
            decision=extracted.decision,
            log=extracted.log
        )
