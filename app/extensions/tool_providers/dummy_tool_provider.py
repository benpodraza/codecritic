from ...abstract_classes.tool_provider_base import ToolProviderBase


class DummyToolProvider(ToolProviderBase):
    def _run(self, *args, **kwargs):
        self._log.info("Dummy tool run")
        return True
