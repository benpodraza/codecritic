from app.factories.base_provider_factory import BaseProviderFactory
from app.db.models import ContextProviderConfig
from app.providers.context_provider_base import ContextProviderBase
from app.enums.logging_enums import RunContext


class ContextProviderFactory(BaseProviderFactory):
    config_model = ContextProviderConfig
    base_class = ContextProviderBase

    @classmethod
    def create(
        cls,
        id: int,
        *,
        context: RunContext,
        **kwargs
    ) -> ContextProviderBase:
        from app.factories.score_provider_factory import ScoreProviderFactory
        from app.factories.tool_provider_factory import ToolProviderFactory

        instance = super().create(id, context=context)
        config = instance._config.config or {}
        provider_id = instance._config.id
        provider_type = instance._infer_provider_type()

        # ─── Child context for subproviders ─────────────────────────────
        child_context = RunContext(
            called_by_type=provider_type,
            called_by_id=provider_id,
            session_id=context.session_id,
            file_log_id=context.file_log_id,
            parent_id=instance._run_id,
            execution_chain=context.execution_chain.copy()
        )

        if (score_id := config.get("score_provider_id")):
            if isinstance(score_id, int) and score_id > 0:
                score = ScoreProviderFactory.create(
                    score_id,
                    context=child_context
                )
                instance.set_score_provider(score)
                if hasattr(score, "set_context_provider"):
                    score.set_context_provider(instance)

        for _, tool_id in (config.get("tool_provider_ids") or {}).items():
            tool = ToolProviderFactory.create(
                tool_id,
                context=child_context
            )
            instance.set_tool_provider(tool)

        return instance
