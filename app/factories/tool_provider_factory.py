from app.factories.base_provider_factory import BaseProviderFactory
from app.db.models import ToolProviderConfig
from app.providers.tool_provider_base import ToolProviderBase


class ToolProviderFactory(BaseProviderFactory):
    config_model = ToolProviderConfig
    base_class = ToolProviderBase