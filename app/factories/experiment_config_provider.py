from __future__ import annotations

from typing import Dict, Any

_CONFIGS: Dict[int, Dict[str, Any]] = {}


class ExperimentConfigProvider:
    """Simple provider storing experiment configurations in memory."""

    @staticmethod
    def register(config_id: int, config: Dict[str, Any]) -> None:
        _CONFIGS[config_id] = config

    @staticmethod
    def load(config_id: int) -> Dict[str, Any]:
        config = _CONFIGS.get(config_id)
        if config is None:
            raise KeyError(f"experiment config {config_id} not found")
        return config
