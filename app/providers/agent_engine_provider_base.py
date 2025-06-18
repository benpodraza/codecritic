from __future__ import annotations
from abc import abstractmethod
from pathlib import Path
from app.db.schemas import AgentEngineOutput
from app.enums.logging_enums import RunContext
from app.enums.agent_enums import AGENT
from app.providers.base_provider import BaseProvider


class AgentEngineProviderBase(BaseProvider):
    def __init__(
        self,
        config=None,
        prompt_provider=None,
        context_provider=None,
        score_provider=None,
        tool_providers=None,
        context: RunContext = None,
        **kwargs
    ):
        super().__init__(config=config, context=context, **kwargs)
        self.prompt_provider = prompt_provider
        self.context_provider = context_provider
        self.score_provider = score_provider
        self.tool_providers = tool_providers or []

    def _run_provider(self, input: dict) -> AgentEngineOutput:

        output = self._run(input=input, context=self.fork_context())

        if not isinstance(output, AgentEngineOutput):
            raise ValueError("Expected AgentEngineOutput from _run")

        if not output.content or not output.decision or not output.log:
            self._log.error("❌ Extraction failed: missing one or more required fields in AgentEngineOutput")
            raise ValueError("Extraction failed: missing content or decision or log entry")

        return output


    @abstractmethod
    def _run(self, input: dict, context: RunContext | None = None) -> AgentEngineOutput:
        raise NotImplementedError
