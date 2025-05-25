from app.factories.base_provider_factory import BaseProviderFactory
from app.db.models import ScoreProviderConfig
from app.providers.score_provider_base import ScoreProviderBase


class ScoreProviderFactory(BaseProviderFactory):
    config_model = ScoreProviderConfig
    base_class = ScoreProviderBase