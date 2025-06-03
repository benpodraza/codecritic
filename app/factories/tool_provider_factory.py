from app.factories.base_provider_factory import BaseProviderFactory
from app.db.models import ToolProviderConfig
from app.providers.tool_provider_base import ToolProviderBase
from app.enums.logging_enums import PROVIDER_TYPE


class ToolProviderFactory(BaseProviderFactory):
    config_model = ToolProviderConfig
    base_class = ToolProviderBase

    @classmethod
    def create(
        cls,
        id: int,
        *,
        called_by_type: PROVIDER_TYPE | None = None,
        called_by_id: int | None = None,
        **kwargs
    ) -> ToolProviderBase:
        instance = super().create(
            id,
            called_by_type=called_by_type,
            called_by_id=called_by_id,
            **kwargs
        )
        config = instance._config.config or {}
        provider_id = instance._config.id
        provider_type = instance._infer_provider_type()

        # ⏱️ Delayed imports to avoid circular dependencies
        if "context_provider_id" in config or "score_provider_id" in config:
            from app.factories.context_provider_factory import ContextProviderFactory
            from app.factories.score_provider_factory import ScoreProviderFactory

            if (ctx_id := config.get("context_provider_id")):
                context = ContextProviderFactory.create(
                    ctx_id,
                    called_by_type=provider_type,
                    called_by_id=provider_id
                )
                instance.set_context_provider(context)
                if hasattr(context, "set_tool_provider"):
                    context.set_tool_provider(instance)

            if (score_id := config.get("score_provider_id")):
                if isinstance(score_id, int) and score_id > 0:
                    score = ScoreProviderFactory.create(
                        score_id,
                        called_by_type=provider_type,
                        called_by_id=provider_id
                    )
                    instance.set_score_provider(score)
                    if hasattr(score, "set_tool_provider"):
                        score.set_tool_provider(instance)

        return instance
