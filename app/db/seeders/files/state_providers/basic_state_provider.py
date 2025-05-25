from app.factories.base_provider_factory import BaseProviderFactory
from app.db.models import StateProviderConfig
from app.providers.state_provider_base import StateProviderBase

class StateProviderFactory(BaseProviderFactory):
    config_model = StateProviderConfig
    base_class = StateProviderBase
