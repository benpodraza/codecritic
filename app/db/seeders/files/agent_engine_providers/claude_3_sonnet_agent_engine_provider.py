import os
import json
import boto3
from app.providers.agent_engine_provider_base import AgentEngineProviderBase


class Claude3SonnetAgentEngineProvider(AgentEngineProviderBase):
    def _run(self, input: dict) -> str:
        prompt = input["prompt"]
        region = os.getenv("AWS_REGION", "us-east-1")

        client = boto3.client("bedrock-runtime", region_name=region)

        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 1024
        }

        response = client.invoke_model(
            modelId="anthropic.claude-3-sonnet-20240229-v1:0",
            contentType="application/json",
            accept="application/json",
            body=json.dumps(body)
        )

        return json.loads(response["body"].read())["content"][0]["text"].strip()
