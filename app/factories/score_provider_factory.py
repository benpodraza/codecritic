from app.factories.base_provider_factory import BaseProviderFactory
from app.db.models import ScoreProviderConfig
from app.providers.score_provider_base import ScoreProviderBase
from app.enums.logging_enums import RunContext


class ScoreProviderFactory(BaseProviderFactory):
    config_model = ScoreProviderConfig
    base_class = ScoreProviderBase

    @classmethod
    def create(
        cls,
        id: int,
        *,
        context: RunContext,
        **kwargs
    ) -> ScoreProviderBase:
        from app.factories.tool_provider_factory import ToolProviderFactory
        from app.factories.context_provider_factory import ContextProviderFactory

        instance = super().create(id, context=context)
        components = instance._components  # provided by BaseProviderFactory
        provider_id = instance._config.id
        provider_type = instance._infer_provider_type()

        # ─── Child context ─────────────────────────────────────────────
        child_context = RunContext(
            called_by_type=provider_type,
            called_by_id=provider_id,
            session_id=context.session_id,
            file_log_id=context.file_log_id,
            parent_id=instance._run_id,
            execution_chain=context.execution_chain.copy()
        )

        if (ctx_id := components.get("context_provider_id")):
            context_provider = ContextProviderFactory.create(
                ctx_id,
                context=child_context
            )
            instance.set_context_provider(context_provider)
            if hasattr(context_provider, "set_score_provider"):
                context_provider.set_score_provider(instance)

        for _, tool_id in (components.get("tool_provider_ids") or {}).items():
            tool = ToolProviderFactory.create(
                tool_id,
                context=child_context
            )
            instance.set_tool_provider(tool)

        return instance
