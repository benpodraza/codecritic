from app.db.models import PromptProviderConfig
from app.factories.base_provider_factory import BaseProviderFactory
from app.providers.prompt_provider_base import PromptProviderBase
from app.utilities.provider_mixin_injector import ProviderContextInjectorWrapper
from app.factories.context_provider_factory import ContextProviderFactory
from pathlib import Path

from app.utilities.run_context import propagate_run_context_if_needed


class PromptProviderFactory(BaseProviderFactory):
    config_model = PromptProviderConfig
    base_class = PromptProviderBase

    @classmethod
    def create(
        cls,
        id: int,
        *,
        called_by_type=None,
        called_by_id=None,
        session_id: str = None,
        file_log_id: str = None,
        **kwargs
    ) -> PromptProviderBase:
        instance = super().create(
            id,
            called_by_type=called_by_type,
            called_by_id=called_by_id,
            **kwargs
        )

        config = instance._config.config or {}
        provider_id = instance._config.id
        provider_type = instance._infer_provider_type()

        def load_prompt(prompt_id: int, table: str) -> str | None:
            if not prompt_id:
                return None
            conn = instance._engine.raw_connection()
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

        agent_prompt_text = load_prompt(config.get("agent_prompt_id"), "agent_prompt")
        system_prompt_text = load_prompt(config.get("system_prompt_id"), "system_prompt")

        context_provider = None
        if config.get("context_provider_id"):
            context_provider = ContextProviderFactory.create(
                config["context_provider_id"],
                called_by_type=provider_type,
                called_by_id=provider_id,
                session_id=session_id,
                file_log_id=file_log_id,
            )

        cls_type = type(instance)
        final_instance = cls_type(
            config=instance._config,
            called_by_type=called_by_type,
            called_by_id=called_by_id,
            agent_text=agent_prompt_text,
            system_text=system_prompt_text,
            context_provider=context_provider,
        )

        propagate_run_context_if_needed(instance)

        return ProviderContextInjectorWrapper(
            final_instance,
            session_id=session_id,
            file_log_id=file_log_id,
        )