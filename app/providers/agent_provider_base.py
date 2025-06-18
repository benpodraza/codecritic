from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from abc import abstractmethod
from sqlalchemy.orm import Session

from app.db.schemas import AgentConversationLogSchema, AgentOutputSchema
from app.enums.logging_enums import LOG_TYPE, RunContext
from app.enums.agent_enums import AGENT
from app.providers.base_provider import BaseProvider


class AgentProviderBase(BaseProvider):
    def __init__(
        self,
        config=None,
        agent_engine=None,
        prompt_provider=None,
        context_provider=None,
        score_provider=None,
        tool_providers=None,
        context: RunContext = None,
        **kwargs
    ):
        super().__init__(config=config, context=context, **kwargs)
        self._agent_engine = agent_engine
        self._prompt_provider = prompt_provider
        self._context_provider = context_provider
        self._score_provider = score_provider
        self._tool_providers = tool_providers or []

    def _run_provider(self, input: dict) -> AgentOutputSchema:
        context = self.fork_context()
        output = self._run(input=input, context=context)
        if not hasattr(output, "score") or output.score is None:
            output.score = -1.0

        self._log.debug(f"\U0001f9fb _run_provider called for: {self._config.name if self._config else 'unknown'}")

        # Log conversation
        log_content = getattr(output, "log", None)
        if log_content:
            self.logger.write(LOG_TYPE.AGENT_CONVERSATION, AgentConversationLogSchema(
                session_id=self._session_id,
                file_log_id=self._file_log_id,
                agent_type=self._config.agent_type if hasattr(self._config, "agent_type") else AGENT.UNKNOWN,
                agent_provider_config_id=self._config.id if self._config else -1,
                content=log_content,
                timestamp=datetime.now(timezone.utc),
            ))
            self._log.debug("✅ AGENT_CONVERSATION log write complete")

        output.agent_type = self._config.agent_type if hasattr(self._config, "agent_type") else AGENT.UNKNOWN
        return output

    @abstractmethod
    def _run(self, input: dict, context: RunContext | None = None) -> AgentOutputSchema:
        raise NotImplementedError
