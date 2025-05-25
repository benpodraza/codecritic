from app.db.models import PromptProviderConfig
from app.factories.base_provider_factory import BaseProviderFactory
from app.providers.prompt_provider_base import PromptProviderBase


class PromptProviderFactory(BaseProviderFactory):
    config_model = PromptProviderConfig
    base_class = PromptProviderBase
