from app.factories.base_provider_factory import BaseProviderFactory
from app.db.models import ContextProviderConfig
from app.providers.context_provider_base import ContextProviderBase
from app.enums.logging_enums import PROVIDER_TYPE
from app.utilities.provider_mixin_injector import ProviderContextInjectorWrapper
from app.utilities.run_context import propagate_run_context_if_needed


class ContextProviderFactory(BaseProviderFactory):
    config_model = ContextProviderConfig
    base_class = ContextProviderBase

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
    ) -> ContextProviderBase:
        from app.factories.score_provider_factory import ScoreProviderFactory
        from app.factories.tool_provider_factory import ToolProviderFactory

        instance = super().create(
            id,
            called_by_type=called_by_type,
            called_by_id=called_by_id,
            **kwargs
        )
        config = instance._config.config or {}
        provider_id = instance._config.id
        provider_type = instance._infer_provider_type()

        if (score_id := config.get("score_provider_id")):
            if isinstance(score_id, int) and score_id > 0:
                score = ScoreProviderFactory.create(
                    score_id,
                    called_by_type=provider_type,
                    called_by_id=provider_id,
                    session_id=session_id,
                    file_log_id=file_log_id
                )
                instance.set_score_provider(score)
                if hasattr(score, "set_context_provider"):
                    score.set_context_provider(instance)

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
