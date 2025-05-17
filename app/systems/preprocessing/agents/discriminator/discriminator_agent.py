# app/systems/preprocessing/agents/discriminator/discriminator_agent.py

from pathlib import Path
from typing import Dict

from jinja2 import Template as JinjaTemplate

from app.utils.base_agent.base_agent import BaseAgent
from app.utils.base_agent.context_provider import ContextProvider
from app.utils.base_agent.tool_provider import ToolProvider
from app.utils.engine.agent_engine_runner import AgentEngineRunner
from app.enums.agent_management_enums import AgentState


class DiscriminatorAgent(BaseAgent):
    """
    DiscriminatorAgent: Evaluates quality of generated code based on linting, typing, and structural analysis.
    Used after Generator in the FSM to assign a code quality score.
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
            name="DiscriminatorAgent",
            prompt_template=prompt_template,
            context_provider=context_provider,
            tool_provider=tool_provider,
            model_payload=model_payload,
            engine=engine
        )

    def run(self, inputs: Dict[str, any]) -> Dict[str, any]:
        self.state = AgentState.RUNNING
        symbol = inputs["symbol"]
        file_path = Path(inputs["file"])

        context = self.context_provider.get_context(inputs)
        if isinstance(self.prompt_template, JinjaTemplate):
            prompt = self.prompt_template.render(**context)
        else:
            prompt = JinjaTemplate(self.prompt_template).render(**context)
        response = self.engine.call_engine(prompt, self.model_payload)

        tool_score = self.tool_provider.get_quality_score(response)
        raw_tools = self.tool_provider.run_all(response)

        self.state = AgentState.COMPLETED
        return {
            "prompt": prompt,
            "response": response,
            "score": tool_score["score"],
            "tools": {k: v.metadata for k, v in raw_tools.items()}
        }


