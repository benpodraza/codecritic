from app.factories.base_provider_factory import BaseProviderFactory
from app.db.models import ScoreProviderConfig
from app.providers.score_provider_base import ScoreProviderBase
from app.enums.logging_enums import PROVIDER_TYPE
from app.utilities.provider_mixin_injector import ProviderContextInjectorWrapper
from app.utilities.run_context import propagate_run_context_if_needed


class ScoreProviderFactory(BaseProviderFactory):
    config_model = ScoreProviderConfig
    base_class = ScoreProviderBase

    @classmethod
    def create(
        cls,
        id: int,
        *,
        called_by_type: PROVIDER_TYPE | None = None,
        called_by_id: int | None = None,
        session_id: str = None,
        file_log_id: str = None,
        **kwargs
    ) -> ScoreProviderBase:
        from app.factories.tool_provider_factory import ToolProviderFactory
        from app.factories.context_provider_factory import ContextProviderFactory

        instance = super().create(
            id,
            called_by_type=called_by_type,
            called_by_id=called_by_id,
            **kwargs
        )
        config = instance._config.config or {}
        provider_id = instance._config.id
        provider_type = instance._infer_provider_type()

        if (ctx_id := config.get("context_provider_id")):
            context = ContextProviderFactory.create(
                ctx_id,
                called_by_type=provider_type,
                called_by_id=provider_id,
                session_id=session_id,
                file_log_id=file_log_id
            )
            instance.set_context_provider(context)
            if hasattr(context, "set_score_provider"):
                context.set_score_provider(instance)

        for _, tool_id in (config.get("tool_provider_ids") or {}).items():
            tool = ToolProviderFactory.create(
                tool_id,
                called_by_type=provider_type,
                called_by_id=provider_id,
                session_id=session_id,
                file_log_id=file_log_id
            )
            instance.set_tool_provider(tool)
        
        propagate_run_context_if_needed(instance)

        return ProviderContextInjectorWrapper(
            instance,
            session_id=session_id,
            file_log_id=file_log_id
        )
