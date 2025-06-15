from app.db.models import AgentEngineProviderConfig
from app.enums.logging_enums import RunContext
from app.factories.base_provider_factory import BaseProviderFactory
from app.providers.agent_engine_provider_base import AgentEngineProviderBase


class AgentEngineProviderFactory(BaseProviderFactory):
    config_model = AgentEngineProviderConfig
    base_class = AgentEngineProviderBase

    @classmethod
    def create(
        cls,
        id: int,
        *,
        context: RunContext,
        **kwargs
    ) -> AgentEngineProviderBase:
        instance = super().create(
            id,
            context=context,
            **kwargs
        )
        return instance
