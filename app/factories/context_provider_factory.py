from app.factories.base_provider_factory import BaseProviderFactory
from app.db.models import ContextProviderConfig
from app.providers.context_provider_base import ContextProviderBase


class ContextProviderFactory(BaseProviderFactory):
    config_model = ContextProviderConfig
    base_class = ContextProviderBase
