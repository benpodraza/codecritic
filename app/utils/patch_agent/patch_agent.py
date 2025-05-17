from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional

from app.utils.base_agent.base_agent import BaseAgent
from app.utils.base_agent.context_provider import ContextProvider
from app.utils.base_agent.tool_provider import ToolProvider
from app.utils.engine.agent_engine_runner import AgentEngineRunner
from app.enums.agent_management_enums import AgentState
from app.utils.logging.log_writers import PromptLogger, ErrorLogger, ConversationLogger
from app.utils.metadata.footer_annotation_helper import strip_metadata_footer, reapply_footer


class PatchAgent(BaseAgent):
    """
    PatchAgent: Applies minimal LLM-driven repairs before full refactor.
    Logs conversation and attaches footer metadata for traceability.
    """

    def __init__(
        self,
        context_provider: ContextProvider,
        tool_provider: ToolProvider,
        engine: AgentEngineRunner,
        model_payload: dict,
        prompt_template: str,
    ):
        super().__init__(
            name="PatchAgent",
            prompt_template=prompt_template,
            context_provider=context_provider,
            tool_provider=tool_provider,
            model_payload=model_payload,
            engine=engine,
        )

    def run(self, inputs: Dict[str, any]) -> Dict[str, any]:
        self.state = AgentState.RUNNING
        start = datetime.now(timezone.utc)

        try:
            context = self.context_provider.get_context(inputs)
            symbol = inputs["symbol"]
            file_path = Path(inputs["file"])
            prompt = self.prompt_template.render(**context)

            raw_code = self.engine.call_engine(prompt, self.model_payload)
            stripped_code, previous_footer = strip_metadata_footer(raw_code)

            new_footer = {
                "agent": self.name,
                "source_file": inputs["file"],
                "annotations_added": ["docstring (if missing)", "logger (if missing)"],
                "modifications": ["bare-except fix"],
                "date": datetime.now(timezone.utc).isoformat(),
                "experiment_id": inputs["experiment_id"],
                "round": inputs["round"]
            }

            annotated_code = reapply_footer(stripped_code, previous_footer, new_footer)
            stop = datetime.now(timezone.utc)

            # ✅ PROMPT LOG
            PromptLogger(inputs["log_path"]).log(
                experiment_id=inputs["experiment_id"],
                run_id=inputs["run_id"],
                round=inputs["round"],
                system=inputs["system"],
                agent_role=self.name,
                agent_engine=self.model_payload.get("model", "unknown"),
                symbol=symbol,
                prompt=prompt,
                response=annotated_code,
                start=start,
                stop=stop,
            )

            # ✅ CONVERSATION LOG
            ConversationLogger(inputs["log_path"]).log(
                experiment_id=inputs["experiment_id"],
                run_id=inputs["run_id"],
                round=inputs["round"],
                agent_role=self.name,
                target=symbol,
                content="Applied patching fix via prompt injection.",
                originating_agent=self.name,
            )

            self.state = AgentState.COMPLETED
            return {
                "prompt": prompt,
                "response": annotated_code
            }

        except Exception as e:
            # ✅ ERROR LOG
            ErrorLogger(inputs["log_path"]).log(
                experiment_id=inputs["experiment_id"],
                run_id=inputs["run_id"],
                round=inputs["round"],
                error_type=type(e).__name__,
                message=f"{str(e)}\n\nAgent: {self.name}\nSymbol: {inputs.get('symbol')}",
                file_path=inputs.get("file", "unknown"),
            )
            raise
