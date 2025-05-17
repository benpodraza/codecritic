from abc import ABC
from typing import Any, Callable, Optional, Dict
from datetime import datetime, timezone

from app.utils.agents.base_agent.context_provider import ContextProvider
from app.utils.agents.base_agent.tool_provider import ToolProvider
from app.utils.agents.engine.agent_engine_runner import AgentEngineRunner
from app.enums.agent_management_enums import AgentState
from app.utils.metadata.logging.log_writers import PromptLogger, ErrorLogger

class BaseAgent(ABC):
    """
    BaseAgent: Abstract base class for all LLM-driven agents with FSM compatibility and full logging.

    Parameters:
        name: Display/logging name of the agent
        prompt_template: Jinja or format-style string for prompt construction
        context_provider: ContextProvider subclass that returns the prompt dictionary
        model_payload: Dict with model, temperature, system role, etc.
        tools: Optional callable toolset
        engine: AgentEngineRunner instance (e.g. OpenAI, Claude)
    """

    def __init__(
        self,
        name: str,
        prompt_template: str,
        context_provider: ContextProvider,
        tool_provider: Optional[ToolProvider] = None,
        model_payload: Optional[Dict[str, Any]] = None,
        tools: Optional[Dict[str, Callable]] = None,
        engine: Optional[AgentEngineRunner] = None,
    ):
        self.name = name
        self.prompt_template = prompt_template
        self.context_provider = context_provider
        self.tool_provider = tool_provider
        self.model_payload = model_payload or {}
        self.tools = tools or {}
        self.engine = engine
        self.state = AgentState.IDLE

        if not self.engine:
            raise ValueError("Agent must be initialized with a valid AgentEngineRunner.")

    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Runs the agent using a formatted prompt, logs PromptLog or ErrorLog accordingly.
        """
        self.state = AgentState.RUNNING
        start_time = datetime.now(timezone.utc)

        try:
            context = self.context_provider.get_context(inputs)
            prompt = self.prompt_template.format(**context)
            response = self.engine.call_engine(prompt, self.model_payload)
            stop_time = datetime.now(timezone.utc)

            # Prompt log
            PromptLogger(inputs["log_path"]).log(
                experiment_id=inputs["experiment_id"],
                run_id=inputs["run_id"],
                round=inputs["round"],
                system=inputs["system"],
                agent_role=self.name,
                agent_engine=self.model_payload.get("model", "unknown"),
                symbol=inputs["symbol"],
                prompt=prompt,
                response=response,
                start=start_time,
                stop=stop_time
            )

            self.state = AgentState.COMPLETED
            return {
                "agent": self.name,
                "input": inputs,
                "response": response
            }

        except Exception as e:
            # Error log with partial info
            ErrorLogger(inputs["log_path"]).log(
                experiment_id=inputs["experiment_id"],
                run_id=inputs["run_id"],
                round=inputs["round"],
                error_type=type(e).__name__,
                message=f"{str(e)}\n\nAgent: {self.name}\nSymbol: {inputs.get('symbol')}\nTemplate: {self.prompt_template[:100]}...",
                file_path=inputs.get("file", "unknown"),
            )
            raise
