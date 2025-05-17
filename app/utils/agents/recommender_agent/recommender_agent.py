from datetime import datetime, timezone
from typing import Dict
from pathlib import Path

from app.utils.agents.base_agent.base_agent import BaseAgent
from app.utils.agents.base_agent.context_provider import ContextProvider
from app.utils.agents.base_agent.tool_provider import ToolProvider
from app.utils.agents.engine.agent_engine_runner import AgentEngineRunner
from app.enums.agent_management_enums import AgentState
from app.utils.metadata.logging.log_writers import ConversationLogger


class RecommenderAgent(BaseAgent):
    """
    RecommenderAgent: Placeholder agent that emits fixed guidance or ranking logic
    to steer future refinement passes. Will later evolve into a learning agent.
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
            name="RecommenderAgent",
            prompt_template=prompt_template,
            context_provider=context_provider,
            tool_provider=tool_provider,
            model_payload=model_payload,
            engine=engine
        )

    def run(self, inputs: Dict[str, any]) -> Dict[str, any]:
        self.state = AgentState.RUNNING
        symbol = inputs["symbol"]

        context = self.context_provider.get_context(inputs)
        prompt = self.prompt_template.render(**context)
        response = self.engine.call_engine(prompt, self.model_payload)

        ConversationLogger(inputs["log_path"]).log(
            experiment_id=inputs["experiment_id"],
            run_id=inputs["run_id"],
            round=inputs["round"],
            agent_role=self.name,
            target=symbol,
            content=response,
            originating_agent=self.name,
        )

        self.state = AgentState.COMPLETED
        return {
            "prompt": prompt,
            "response": response
        }
