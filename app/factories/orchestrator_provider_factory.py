from app.factories.base_provider_factory import BaseProviderFactory
from app.db.models import OrchestratorProviderConfig
from app.providers.orchestrator_provider_base import OrchestratorProviderBase


class OrchestratorProviderFactory(BaseProviderFactory):
    config_model = OrchestratorProviderConfig
    base_class = OrchestratorProviderBase