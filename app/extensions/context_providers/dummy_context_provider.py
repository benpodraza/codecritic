from ...abstract_classes.context_provider_base import ContextProviderBase


class DummyContextProvider(ContextProviderBase):
    def _get_context(self, *args, **kwargs):
        self.logger.info("Dummy context provided")
        return {}
