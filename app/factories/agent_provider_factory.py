from app.factories.base_provider_factory import BaseProviderFactory
from app.db.models import AgentProviderConfig
from app.providers.agent_provider_base import AgentProviderBase
from app.enums.logging_enums import PROVIDER_TYPE, RunContext


class AgentProviderFactory(BaseProviderFactory):
    config_model = AgentProviderConfig
    base_class = AgentProviderBase

    @classmethod
    def create(
        cls,
        id: int,
        *,
        context: RunContext,
        **kwargs
    ) -> AgentProviderBase:
        from app.factories.agent_engine_provider_factory import AgentEngineProviderFactory
        from app.factories.prompt_provider_factory import PromptProviderFactory
        from app.factories.context_provider_factory import ContextProviderFactory
        from app.factories.score_provider_factory import ScoreProviderFactory
        from app.factories.tool_provider_factory import ToolProviderFactory

        preload_instance = super().create(id, context=context)

        # ✅ Use already-injected structured config
        components = preload_instance._components
        provider_id = preload_instance._config.id
        provider_type = preload_instance._infer_provider_type()

        # ─── Child context ─────────────────────────────────────────────
        child_context = RunContext(
            called_by_type=provider_type,
            called_by_id=provider_id,
            session_id=context.session_id,
            file_log_id=context.file_log_id,
            parent_id=preload_instance._run_id,
            execution_chain=context.execution_chain.copy()
        )

        # ─── Create subproviders ───────────────────────────────────────
        agent_engine = (
            AgentEngineProviderFactory.create(
                components["agent_engine_provider_id"],
                context=child_context,
            ) if components.get("agent_engine_provider_id") else None
        )

        prompt_provider = (
            PromptProviderFactory.create(
                components["prompt_provider_id"],
                context=child_context,
            ) if components.get("prompt_provider_id") else None
        )

        context_provider = (
            ContextProviderFactory.create(
                components["context_provider_id"],
                context=child_context,
            ) if components.get("context_provider_id") else None
        )

        score_provider = (
            ScoreProviderFactory.create(
                components["score_provider_id"],
                context=child_context,
            ) if components.get("score_provider_id") else None
        )

        tool_providers = [
            ToolProviderFactory.create(
                tid,
                context=child_context,
            )
            for tid in (components.get("tool_provider_ids") or {}).values()
        ]

        # ─── Final instance construction ───────────────────────────────
        cls_type = type(preload_instance)
        return cls_type(
            config=preload_instance._config,
            agent_engine=agent_engine,
            prompt_provider=prompt_provider,
            context_provider=context_provider,
            score_provider=score_provider,
            tool_providers=tool_providers,
            context=context
        )
