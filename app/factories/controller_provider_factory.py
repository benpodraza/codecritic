from app.factories.base_provider_factory import BaseProviderFactory
from app.db.models import ControllerProviderConfig
from app.providers.controller_provider_base import ControllerProviderBase

class ControllerProviderFactory(BaseProviderFactory):
    config_model = ControllerProviderConfig
    base_class   = ControllerProviderBase

    @classmethod
    def create(cls, id: int, **kwargs) -> ControllerProviderBase:
        from app.factories.context_provider_factory import ContextProviderFactory
        from app.factories.score_provider_factory   import ScoreProviderFactory
        from app.factories.tool_provider_factory    import ToolProviderFactory

        inst   = super().create(id)
        config = inst.config.config or {}

        ctx   = (
            ContextProviderFactory.create(config["context_provider_id"])
            if config.get("context_provider_id") else None
        )
        scr   = (
            ScoreProviderFactory.create(config["score_provider_id"])
            if config.get("score_provider_id") else None
        )
        tools = [
            ToolProviderFactory.create(tid)
            for tid in (config.get("tool_provider_ids") or {}).values()
        ]

        cls_type = type(inst)
        return cls_type(
            config           = inst.config,
            engine           = inst._engine,
            context_provider = ctx,
            score_provider   = scr,
            tool_providers   = tools,
        )
