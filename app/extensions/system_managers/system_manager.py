from __future__ import annotations

from typing import List

from ...abstract_classes.system_manager_base import SystemManagerBase
from ...enums.system_enums import SystemState, StateTransitionReason
from ...factories.agent import AgentFactory
from ...factories.context_provider import ContextProviderFactory
from ...factories.prompt_manager import PromptGeneratorFactory
from ...factories.logging_provider import (
    CodeQualityLog,
    PromptLog,
    ScoringLog,
    StateLog,
    StateTransitionLog,
    LoggingProvider,
)
from ..state_managers.state_manager import StateManager


class SystemManager(SystemManagerBase):
    def __init__(self, logger: LoggingProvider | None = None) -> None:
        super().__init__(logger)
        self.state_manager = StateManager(logger=logger)
        self.current_state = SystemState.START
        self.transition_logs: List[StateTransitionLog] = []
        self.state_logs: List[StateLog] = []
        self.prompt_logs: List[PromptLog] = []
        self.code_quality_logs: List[CodeQualityLog] = []
        self.scoring_logs: List[ScoringLog] = []

        self.context_provider = ContextProviderFactory.create(
            "symbol_graph", module_path="sample_module.py"
        )
        self.prompt_generator = PromptGeneratorFactory.create(
            "basic", context_provider=self.context_provider
        )
        self.generator = AgentFactory.create(
            "generator",
            target="sample_module.py",
            logger=logger,
            snapshot_writer=None,
        )
        self.evaluator = AgentFactory.create(
            "evaluator",
            target="sample_module.py",
            logger=logger,
        )

    def _transition_to(
        self, next_state: SystemState, reason: StateTransitionReason
    ) -> None:
        self.state_manager.transition_state(
            experiment_id="exp",
            round=0,
            from_state=self.current_state,
            to_state=next_state,
            reason=reason,
        )
        self.transition_logs.append(self.state_manager.transition_logs[-1])
        self.current_state = next_state

    def _run_system_logic(self, *args, **kwargs) -> None:
        sequence = [
            SystemState.GENERATE,
            SystemState.DISCRIMINATE,
            SystemState.MEDIATE,
            SystemState.PATCH,
            SystemState.EVALUATE,
            SystemState.END,
        ]
        for state in sequence:
            self._transition_to(state, reason=StateTransitionReason.FIRST_ROUND)
            if state is not SystemState.END:
                self.state_manager.run_state(
                    experiment_id="exp",
                    system="system",
                    round=0,
                    state=state,
                    action="run",
                )
                self.state_logs.append(self.state_manager.state_logs[-1])
                if state == SystemState.GENERATE:
                    self.generator.run()
                    self.prompt_logs.extend(self.generator.prompt_logs)
                elif state == SystemState.DISCRIMINATE:
                    self.evaluator.run()
                    self.code_quality_logs.extend(self.evaluator.quality_logs)

        for pr in self.prompt_logs:
            self.log_prompt(pr)
        for cq in self.code_quality_logs:
            self.log_code_quality(cq)
        for sc in self.scoring_logs:
            self.log_scoring(sc)
