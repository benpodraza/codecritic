import os, json, boto3
from app.db.schemas import AgentEngineOutput
from app.providers.agent_engine_provider_base import AgentEngineProviderBase

class Claude3SonnetAgentEngineProvider(AgentEngineProviderBase):
    def _run(self, input: dict) -> AgentEngineOutput:
        prompt = input["prompt"]
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

        content = json.loads(response_raw["body"].read())["content"][0]["text"].strip()
        token_count = len(content.split())
        cost_usd = token_count * (self._config.cost_per_1k_tokens or 0.0) / 1000

        return AgentEngineOutput(response=content, token_count=token_count, cost_usd=cost_usd)
