from __future__ import annotations

from abc import abstractmethod

from app.providers.base_provider import BaseProvider
from app.utilities.metadata.snapshots.snapshot_writer import SnapshotWriter

class AgentProviderBase(BaseProvider):
    """Agent provider that wraps _run with snapshot logic."""

    def _run_provider(self, input: dict) -> str:
        output = self._run(input)
        if "before" in (self.config.config or {}):
            self._snapshot_id = SnapshotWriter().write_snapshot(
                before=self.config.config.get("before"),
                after=output
            )
        return output

    @abstractmethod
    def _run(self, input: dict) -> str:
        raise NotImplementedError
