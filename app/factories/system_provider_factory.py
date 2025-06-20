from app.factories.base_provider_factory import BaseProviderFactory
from app.db.models import SystemProviderConfig
from app.providers.system_provider_base import SystemProviderBase
from app.enums.logging_enums import RunContext


class SystemProviderFactory(BaseProviderFactory):
    config_model = SystemProviderConfig
    base_class = SystemProviderBase

    @classmethod
    def create(
        cls,
        id: int,
        *,
        context: RunContext,
        **kwargs
    ) -> SystemProviderBase:
        # ⏱️ Delayed imports to avoid circular dependencies
        from app.factories.state_provider_factory import StateProviderFactory
        from app.factories.context_provider_factory import ContextProviderFactory
        from app.factories.score_provider_factory import ScoreProviderFactory
        from app.factories.tool_provider_factory import ToolProviderFactory

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

        # ─── Subproviders ──────────────────────────────────────────────
        context_provider = (
            ContextProviderFactory.create(
                components["context_provider_id"],
                context=child_context
            ) if components.get("context_provider_id") else None
        )

        score_provider = (
            ScoreProviderFactory.create(
                components["score_provider_id"],
                context=child_context
            ) if components.get("score_provider_id") else None
        )

        tool_providers = [
            ToolProviderFactory.create(
                tool_id,
                context=child_context
            )
            for _, tool_id in (components.get("tool_provider_ids") or {}).items()
        ]

        state_providers = {
            name: StateProviderFactory.create(
                state_id,
                context=child_context
            )
            for name, state_id in (components.get("states") or {}).items()
        }

        # ─── Final instantiation ───────────────────────────────────────
        cls_type = type(preload_instance)
        return cls_type(
            config=preload_instance._config,
            context_provider=context_provider,
            score_provider=score_provider,
            tool_providers=tool_providers,
            state_providers=state_providers,
            context=context
        )
