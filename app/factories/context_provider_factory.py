from app.factories.base_provider_factory import BaseProviderFactory
from app.db.models import ContextProviderConfig
from app.providers.context_provider_base import ContextProviderBase

class ContextProviderFactory(BaseProviderFactory):
    config_model = ContextProviderConfig
    base_class = ContextProviderBase

    @classmethod
    def create(cls, id: int, **kwargs) -> ContextProviderBase:
        instance = super().create(id, **kwargs)
        config = instance.config.config or {}

        # ⏱️ Delayed imports to avoid circular dependencies
        if "score_provider_id" in config or "tool_provider_ids" in config:
            from app.factories.score_provider_factory import ScoreProviderFactory
            from app.factories.tool_provider_factory import ToolProviderFactory

            if (score_id := config.get("score_provider_id")):
                if isinstance(score_id, int) and score_id > 0:
                    score = ScoreProviderFactory.create(score_id)
                    instance.set_score_provider(score)

            for _, tool_id in (config.get("tool_provider_ids") or {}).items():
                tool = ToolProviderFactory.create(tool_id)
                instance.set_tool_provider(tool)

        return instance
