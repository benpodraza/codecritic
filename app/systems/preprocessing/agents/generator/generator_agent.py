# app/systems/preprocessing/agents/generator/generator_agent.py

from pathlib import Path
from typing import Dict
from jinja2 import Template as JinjaTemplate

from app.utils.base_agent.base_agent import BaseAgent
from app.utils.base_agent.context_provider import ContextProvider
from app.utils.base_agent.tool_provider import ToolProvider
from app.utils.engine.agent_engine_runner import AgentEngineRunner
from app.enums.agent_management_enums import AgentState


class GeneratorAgent(BaseAgent):
    """
    GeneratorAgent: Produces transformed/refactored versions of source code.
    Typically the first step in the FSM round.
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
            name="GeneratorAgent",
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

        formatted = self.tool_provider.run_tool("black", response)
        docstringed = self.tool_provider.run_tool("docformatter", formatted.output)

        self.state = AgentState.COMPLETED
        return {
            "prompt": prompt,
            "response": docstringed.output,
            "tools": {
                "black": formatted.metadata,
                "docformatter": docstringed.metadata
            }
        }