from app.factories.base_provider_factory import BaseProviderFactory
from app.db.models import ToolProviderConfig
from app.providers.tool_provider_base import ToolProviderBase
from app.enums.logging_enums import RunContext


class ToolProviderFactory(BaseProviderFactory):
    config_model = ToolProviderConfig
    base_class = ToolProviderBase

    @classmethod
    def create(
        cls,
        id: int,
        *,
        context: RunContext,
        **kwargs
    ) -> ToolProviderBase:
        from app.factories.context_provider_factory import ContextProviderFactory
        from app.factories.score_provider_factory import ScoreProviderFactory

        preload_instance = super().create(id, context=context)
        components = preload_instance._components
        provider_id = preload_instance._config.id
        provider_type = preload_instance._provider_type

        # ─── Child context ─────────────────────────────────────────────
        child_context = RunContext(
            called_by_type=provider_type,
            called_by_id=provider_id,
            session_id=context.session_id,
            file_log_id=context.file_log_id,
            parent_id=preload_instance._run_id,
            execution_chain=context.execution_chain.copy()
        )

        if (ctx_id := components.get("context_provider_id")):
            context_provider = ContextProviderFactory.create(
                ctx_id,
                context=child_context
            )
            preload_instance.set_context_provider(context_provider)
            if hasattr(context_provider, "set_tool_provider"):
                context_provider.set_tool_provider(preload_instance)

        if (score_id := components.get("score_provider_id")):
            if isinstance(score_id, int) and score_id > 0:
                score_provider = ScoreProviderFactory.create(
                    score_id,
                    context=child_context
                )
                preload_instance.set_score_provider(score_provider)
                if hasattr(score_provider, "set_tool_provider"):
                    score_provider.set_tool_provider(preload_instance)

        return preload_instance
