from __future__ import annotations

from typing import List

from ...factories.agent import AgentFactory
from ...factories.context_provider import ContextProviderFactory
from ...factories.prompt_manager import PromptGeneratorFactory
from ...utilities.db import init_db, insert_logs
from ...utilities.metadata.logging import (
    CodeQualityLog,
    PromptLog,
    ScoringLog,
    StateLog,
    StateTransitionLog,
)

from ...abstract_classes.system_manager_base import SystemManagerBase
from ...enums.system_enums import FSMState
from ..state_managers.state_manager import StateManager


class SystemManager(SystemManagerBase):
    """Concrete system manager implementing FSM transitions."""

    def __init__(self) -> None:
        super().__init__()
        self.state_manager = StateManager()
        self.current_state = FSMState.START
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
        self.generator = AgentFactory.create("generator", target="sample_module.py")
        self.evaluator = AgentFactory.create("evaluator", target="sample_module.py")

    def _transition_to(self, next_state: FSMState, reason: str | None = None) -> None:
        log = StateTransitionLog(
            experiment_id="exp",
            round=0,
            from_state=self.current_state.value,
            to_state=next_state.value,
            reason=reason,
        )
        self.transition_logs.append(log)
        self.logger.info("%s -> %s", self.current_state.value, next_state.value)
        self.current_state = next_state

    def _run_system_logic(self, *args, **kwargs) -> None:
        sequence = [
            FSMState.GENERATE,
            FSMState.DISCRIMINATE,
            FSMState.MEDIATE,
            FSMState.PATCHOR,
            FSMState.RECOMMENDER,
            FSMState.END,
        ]
        conn = init_db()
        for state in sequence:
            self._transition_to(state)
            if state is not FSMState.END:
                self.state_manager.run(state=state.value)
                self.state_logs.append(
                    StateLog(
                        experiment_id="exp",
                        system="system",
                        round=0,
                        state=state.value,
                        action="run",
                    )
                )
                if state is FSMState.GENERATE:
                    self.generator.run()
                    self.prompt_logs.extend(self.generator.prompt_logs)
                elif state is FSMState.DISCRIMINATE:
                    self.evaluator.run()
                    self.code_quality_logs.extend(self.evaluator.quality_logs)

        insert_logs(conn, "state_transition_log", self.transition_logs)
        insert_logs(conn, "state_log", self.state_logs)
        insert_logs(conn, "prompt_log", self.prompt_logs)
        insert_logs(conn, "code_quality_log", self.code_quality_logs)
        if self.scoring_logs:
            insert_logs(conn, "scoring_log", self.scoring_logs)
        conn.close()
