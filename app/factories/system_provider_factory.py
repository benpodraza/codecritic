from app.factories.base_provider_factory import BaseProviderFactory
from app.db.models import SystemProviderConfig
from app.providers.system_provider_base import SystemProviderBase
from app.enums.logging_enums import PROVIDER_TYPE


class SystemProviderFactory(BaseProviderFactory):
    config_model = SystemProviderConfig
    base_class = SystemProviderBase

    @classmethod
    def create(
        cls,
        id: int,
        *,
        called_by_type: PROVIDER_TYPE | None = None,
        called_by_id: int | None = None,
        **kwargs
    ) -> SystemProviderBase:
        # ⏱️ Delayed imports to avoid circular dependencies
        from app.factories.state_provider_factory import StateProviderFactory
        from app.factories.context_provider_factory import ContextProviderFactory
        from app.factories.score_provider_factory import ScoreProviderFactory
        from app.factories.tool_provider_factory import ToolProviderFactory

        preload_instance = super().create(
            id,
            called_by_type=called_by_type,
            called_by_id=called_by_id,
            **kwargs
        )

        config = preload_instance._config.config or {}
        provider_id = preload_instance._config.id
        provider_type = preload_instance._infer_provider_type()

        context_provider = (
            ContextProviderFactory.create(
                config["context_provider_id"],
                called_by_type=provider_type,
                called_by_id=provider_id
            ) if config.get("context_provider_id") else None
        )

        score_provider = (
            ScoreProviderFactory.create(
                config["score_provider_id"],
                called_by_type=provider_type,
                called_by_id=provider_id
            ) if config.get("score_provider_id") else None
        )

        tool_providers = [
            ToolProviderFactory.create(
                tool_id,
                called_by_type=provider_type,
                called_by_id=provider_id
            )
            for _, tool_id in (config.get("tool_provider_ids") or {}).items()
        ]

        state_providers = {
            name: StateProviderFactory.create(
                state_id,
                called_by_type=provider_type,
                called_by_id=provider_id
            )
            for name, state_id in (config.get("states") or {}).items()
        }

        cls_type = type(preload_instance)
        return cls_type(
            config=preload_instance._config,
            context_provider=context_provider,
            score_provider=score_provider,
            tool_providers=tool_providers,
            state_providers=state_providers,
            called_by_type=called_by_type,
            called_by_id=called_by_id,
        )
