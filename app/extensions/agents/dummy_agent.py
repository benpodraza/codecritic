from ...abstract_classes.agent_base import AgentBase


class DummyAgent(AgentBase):
    def _run_agent_logic(self, *args, **kwargs) -> None:
        self._log.info("Dummy agent logic executed")
