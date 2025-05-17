from .. import Registry

SCORING_MODEL_REGISTRY = Registry()

try:  # pragma: no cover - optional seed import
    from ...extensions.scoring_models.dummy_scoring_provider import (
        DummyScoringProvider,
    )

    SCORING_MODEL_REGISTRY.register("dummy", DummyScoringProvider)
except Exception:  # pragma: no cover - ignore failures during optional import
    pass
