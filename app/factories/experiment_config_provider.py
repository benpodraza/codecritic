from __future__ import annotations

from typing import Dict, Any

_CONFIGS: Dict[str, Dict[str, Any]] = {}


class ExperimentConfigProvider:
    """Simple provider storing experiment configurations in memory."""

    @staticmethod
    def register(config_id: int | str, config: Dict[str, Any]) -> None:
        _CONFIGS[str(config_id)] = config

    @staticmethod
    def load(config_id: int | str) -> Dict[str, Any]:
        config = _CONFIGS.get(str(config_id))
        if config is None:
            raise KeyError(f"experiment config {config_id} not found")
        return config
