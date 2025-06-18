from app.factories.base_provider_factory import BaseProviderFactory
from app.db.models import ProgramProviderConfig
from app.providers.program_provider_base import ProgramProviderBase
from app.enums.logging_enums import RunContext


class ProgramProviderFactory(BaseProviderFactory):
    config_model = ProgramProviderConfig
    base_class = ProgramProviderBase

    @classmethod
    def create(
        cls,
        id: int,
        *,
        context: RunContext,
        **kwargs
    ) -> ProgramProviderBase:
        from app.factories.context_provider_factory import ContextProviderFactory
        from app.factories.score_provider_factory import ScoreProviderFactory
        from app.factories.tool_provider_factory import ToolProviderFactory
        from app.factories.controller_provider_factory import ControllerProviderFactory

        inst = super().create(id, context=context)
        components = inst._components  # structured access injected by BaseProviderFactory
        provider_id = inst._config.id
        provider_type = inst._infer_provider_type()

        # ─── Child context ─────────────────────────────────────────────
        child_context = RunContext(
            called_by_type=provider_type,
            called_by_id=provider_id,
            session_id=context.session_id,
            file_log_id=context.file_log_id,
            parent_id=inst._run_id,
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
                tid,
                context=child_context
            )
            for tid in (components.get("tool_provider_ids") or {}).values()
        ]

        controller_providers = {
            name: ControllerProviderFactory.create(
                controller_id,
                context=child_context
            )
            for name, controller_id in (components.get("controllers") or {}).items()
        }

        # ─── Final instantiation ───────────────────────────────────────
        cls_type = type(inst)
        instance = cls_type(
            config=inst._config,
            context_provider=context_provider,
            score_provider=score_provider,
            tool_providers=tool_providers,
            controller_providers=controller_providers,
            context=context
        )

        return instance
