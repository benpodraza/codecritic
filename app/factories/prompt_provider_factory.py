from app.db.models import PromptProviderConfig
from app.factories.base_provider_factory import BaseProviderFactory
from app.providers.prompt_provider_base import PromptProviderBase
from app.factories.context_provider_factory import ContextProviderFactory
from app.enums.logging_enums import RunContext
from pathlib import Path


class PromptProviderFactory(BaseProviderFactory):
    config_model = PromptProviderConfig
    base_class = PromptProviderBase

    @classmethod
    def create(
        cls,
        id: int,
        *,
        context: RunContext,
        **kwargs
    ) -> PromptProviderBase:
        preload_instance = super().create(id, context=context)
        components = preload_instance._components  # injected by BaseProviderFactory
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

        # ─── Prompt loading ────────────────────────────────────────────
        def load_prompt(prompt_id: int, table: str) -> str | None:
            if not prompt_id:
                return None
            conn = preload_instance._engine.raw_connection()
            try:
                cur = conn.cursor()
                cur.execute(f"SELECT artifact_path FROM {table} WHERE id = ?", (prompt_id,))
                row = cur.fetchone()
                if row:
                    artifact_path = row[0]
                    if artifact_path:
                        return (Path("extensions") / artifact_path).read_text(encoding="utf-8").strip()
            finally:
                conn.close()
            return None

        agent_prompt_text = load_prompt(components.get("agent_prompt_id"), "agent_prompt")
        system_prompt_text = load_prompt(components.get("system_prompt_id"), "system_prompt")

        context_provider = None
        if components.get("context_provider_id"):
            context_provider = ContextProviderFactory.create(
                components["context_provider_id"],
                context=child_context
            )

        cls_type = type(preload_instance)
        return cls_type(
            config=preload_instance._config,
            agent_text=agent_prompt_text,
            system_text=system_prompt_text,
            context_provider=context_provider,
            context=context
        )
