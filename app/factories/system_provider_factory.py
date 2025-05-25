from app.factories.base_provider_factory import BaseProviderFactory
from app.db.models import SystemProviderConfig
from app.providers.system_provider_base import SystemProviderBase

class SystemProviderFactory(BaseProviderFactory):
    config_model = SystemProviderConfig
    base_class = SystemProviderBase
