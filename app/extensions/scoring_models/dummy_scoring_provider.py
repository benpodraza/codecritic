from ...abstract_classes.scoring_provider_base import ScoringProviderBase


class DummyScoringProvider(ScoringProviderBase):
    def _score(self, *args, **kwargs):
        self.logger.info("Dummy scoring")
        return 0
