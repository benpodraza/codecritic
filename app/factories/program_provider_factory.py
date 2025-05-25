from app.factories.base_provider_factory import BaseProviderFactory
from app.db.models import ProgramProviderConfig
from app.providers.program_provider_base import ProgramProviderBase


class ProgramProviderFactory(BaseProviderFactory):
    config_model = ProgramProviderConfig
    base_class = ProgramProviderBase