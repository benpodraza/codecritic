from app.factories.base_provider_factory import BaseProviderFactory
from app.db.models import ControllerProviderConfig
from app.providers.controller_provider_base import ControllerProviderBase
from app.enums.logging_enums import PROVIDER_TYPE
from app.utilities.provider_mixin_injector import ProviderContextInjectorWrapper
from app.utilities.run_context import propagate_run_context_if_needed


class ControllerProviderFactory(BaseProviderFactory):
    config_model = ControllerProviderConfig
    base_class = ControllerProviderBase

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
    ) -> ControllerProviderBase:
        from app.factories.context_provider_factory import ContextProviderFactory
        from app.factories.score_provider_factory   import ScoreProviderFactory
        from app.factories.tool_provider_factory    import ToolProviderFactory
        from app.factories.system_provider_factory  import SystemProviderFactory

        inst = super().create(
            id,
            called_by_type=called_by_type,
            called_by_id=called_by_id,
            **kwargs
        )
        config = inst._config.config or {}
        provider_id = inst._config.id
        provider_type = inst._infer_provider_type()

        context_provider = (
            ContextProviderFactory.create(
                config["context_provider_id"],
                called_by_type=provider_type,
                called_by_id=provider_id,
                session_id=session_id,
                file_log_id=file_log_id
            ) if config.get("context_provider_id") else None
        )

        score_provider = (
            ScoreProviderFactory.create(
                config["score_provider_id"],
                called_by_type=provider_type,
                called_by_id=provider_id,
                session_id=session_id,
                file_log_id=file_log_id
            ) if config.get("score_provider_id") else None
        )

        tool_providers = [
            ToolProviderFactory.create(
                tid,
                called_by_type=provider_type,
                called_by_id=provider_id,
                session_id=session_id,
                file_log_id=file_log_id
            )
            for tid in (config.get("tool_provider_ids") or {}).values()
        ]

        system_providers = {
            name: SystemProviderFactory.create(
                sys_id,
                called_by_type=provider_type,
                called_by_id=provider_id,
                session_id=session_id,
                file_log_id=file_log_id
            )
            for name, sys_id in (config.get("systems") or {}).items()
        }

        cls_type = type(inst)
        instance = cls_type(
            config           = inst._config,
            context_provider = context_provider,
            score_provider   = score_provider,
            tool_providers   = tool_providers,
            system_providers = system_providers, 
            called_by_type   = called_by_type,
            called_by_id     = called_by_id,
        )

        propagate_run_context_if_needed(instance)

        return ProviderContextInjectorWrapper(
            instance,
            session_id=session_id,
            file_log_id=file_log_id
        )
