from app.db.models import AgentProviderConfig
from app.factories.base_provider_factory import BaseProviderFactory
from app.providers.agent_provider_base import AgentProviderBase


class AgentProviderFactory(BaseProviderFactory):
    config_model = AgentProviderConfig
    base_class = AgentProviderBase
