# app/systems/preprocessing/agents/mediator/mediator_agent.py

from pathlib import Path
from typing import Dict
from jinja2 import Template as JinjaTemplate

from app.utils.agents.base_agent.base_agent import BaseAgent
from app.utils.agents.base_agent.context_provider import ContextProvider
from app.utils.agents.base_agent.tool_provider import ToolProvider
from app.utils.agents.engine.agent_engine_runner import AgentEngineRunner
from app.utils.tools.tool_result import ToolResult
from app.enums.agent_management_enums import AgentState


class MediatorAgent(BaseAgent):
    """
    MediatorAgent: Intervenes when FSM stalls; uses tools and prompt-based reasoning to recommend resets or overrides.
    """

    def __init__(
        self,
        context_provider: ContextProvider,
        tool_provider: ToolProvider,
        engine: AgentEngineRunner,
        model_payload: dict,
        prompt_template: str
    ):
        super().__init__(
            name="MediatorAgent",
            prompt_template=prompt_template,
            context_provider=context_provider,
            tool_provider=tool_provider,
            model_payload=model_payload,
            engine=engine
        )

    def run(self, inputs: Dict[str, any]) -> Dict[str, any]:
        self.state = AgentState.RUNNING
        context = self.context_provider.get_context(inputs)
        if isinstance(self.prompt_template, JinjaTemplate):
            prompt = self.prompt_template.render(**context)
        else:
            prompt = JinjaTemplate(self.prompt_template).render(**context)
        response = self.engine.call_engine(prompt, self.model_payload)

        # Optionally query sonarcloud or pyrefactor here
        sonar_result: ToolResult = self.tool_provider.run_tool("sonarcloud", response)

        self.state = AgentState.COMPLETED
        return {
            "prompt": prompt,
            "response": response,
            "tools": {
                "sonarcloud": sonar_result.metadata
            }
        }
