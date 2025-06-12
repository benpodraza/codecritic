from app.db.models import AgentEngineProviderConfig
from app.factories.base_provider_factory import BaseProviderFactory
from app.providers.agent_engine_provider_base import AgentEngineProviderBase
from app.utilities.provider_mixin_injector import ProviderContextInjectorWrapper


class AgentEngineProviderFactory(BaseProviderFactory):
    config_model = AgentEngineProviderConfig
    base_class = AgentEngineProviderBase

    @classmethod
    def create(
        cls,
        id: int,
        *,
        called_by_type=None,
        called_by_id=None,
        session_id: str = None,
        file_log_id: str = None,
        **kwargs
    ) -> AgentEngineProviderBase:
        instance = super().create(
            id,
            called_by_type=called_by_type,
            called_by_id=called_by_id,
            **kwargs
        )
        return ProviderContextInjectorWrapper(
            instance,
            session_id=session_id,
            file_log_id=file_log_id
        )
