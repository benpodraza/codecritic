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

        # 🔧 Extract components and params from config for consistency (if needed downstream)
        raw_config = instance._config.config or {}
        components = raw_config.get("components") or {}
        params     = raw_config.get("params") or {}

        # Optionally inject into instance if base class expects them split
        instance._components = components
        instance._params = params

        return instance
