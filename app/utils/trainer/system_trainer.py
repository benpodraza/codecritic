# app/utils/evaluation/static_code_evaluator/static_code_evaluator_v1.py

from pathlib import Path
from typing import Optional
from collections import deque
from datetime import datetime, timezone
import json
from app.enums.agent_management_enums import AgentRole
from app.schemas.experiment_config_schemas import ExperimentConfig
from app.systems.preprocessing.utils.tool_provider_preprocessor import ToolProviderPreprocessor
from app.utils.agents.agent_factory.agent_factory import build_agent
from app.utils.experiments.evaluation.evaluator_factory import build_evaluator
from app.utils.experiments.file_management.path_utils import get_experiment_paths
from app.enums.state_transition_enums import TransitionTarget
from app.utils.metadata.footer.footer_annotation_helper import strip_metadata_footer, append_metadata_footer, reapply_footer
from app.utils.metadata.footer.footer_metadata import FooterMetadata
from app.utils.symbol_graph.symbol_service import SymbolService
from app.utils.metadata.logging.log_writers import (
    StateLogger,
    StateTransitionLogger,
    ErrorLogger,
    ExperimentLogger
)
from app.utils.metadata.snapshots.snapshot_writer import RunSnapshotLogger
from app.utils.metadata.logging.log_writers import EvaluationLogger

class SystemTrainer:
    def __init__(
        self,
        experiment_path: Path,
        config: ExperimentConfig
    ):
        self.experiment_path: Path = experiment_path
        self.config: ExperimentConfig = config
        
        
        symbol_service = SymbolService(experiment_path)
        self.generator = build_agent(AgentRole.GENERATOR, config.generator, symbol_service)
        self.discriminator = build_agent(AgentRole.DISCRIMINATOR, config.discriminator, symbol_service)
        self.mediator = build_agent(AgentRole.MEDIATOR, config.mediator, symbol_service)
        self.patchor = build_agent(AgentRole.PATCHOR, config.patchor, symbol_service)
        self.recommender = build_agent(AgentRole.RECOMMENDER, config.recommender, symbol_service)

        
        tool_provider = ToolProviderPreprocessor()
        self.evaluator = build_evaluator(config.evaluator, tool_provider)

        paths = get_experiment_paths(
            experiment_root=experiment_path,
            experiment_id=config.experiment_id,
            run_id=config.run_id
        )

        self.log_dir: Path = paths["log_dir"]
        self.snapshot_dir: Path = paths["snapshot_dir"]
        self.review_dir: Path = paths["review_dir"]
        self.config_path: Path = paths["config_path"]
        self.queue_path: Path = self.log_dir / "pending_queue.json"

        self.state_logger = StateLogger(self.log_dir / "state_log.jsonl")
        self.state_transition_logger = StateTransitionLogger(self.log_dir / "state_transition_log.jsonl")
        self.error_logger = ErrorLogger(self.log_dir / "error_log.jsonl")
        self.experiment_logger = ExperimentLogger(self.log_dir / "experiment_log.jsonl")
        self.snapshot_logger = RunSnapshotLogger(self.snapshot_dir)
        self.evaluation_logger = EvaluationLogger(self.log_dir / "evaluation_log.jsonl")


    def run(self, input_path: Path, output_path: Path, recurse: bool = False):
        print(f"✨ Beginning experiment: {self.config.experiment_id} run {self.config.run_id}")
        queue = deque()

        if self.queue_path.exists():
            print("🔄 Recovering queue from previous run...")
            with self.queue_path.open("r", encoding="utf-8") as f:
                persisted = json.load(f)
                queue.extend((Path(src), Path(dst)) for src, dst in persisted)
        else:
            if input_path.is_file():
                rel_path = input_path.name
                queue.append((input_path, output_path / rel_path))
            elif input_path.is_dir():
                files = input_path.rglob("*.py") if recurse else input_path.glob("*.py")
                for file in files:
                    relative_path = file.relative_to(input_path)
                    queue.append((file, output_path / relative_path))
            else:
                raise FileNotFoundError(f"Input path not found: {input_path}")

            with self.queue_path.open("w", encoding="utf-8") as f:
                json.dump([(str(s), str(d)) for s, d in queue], f, indent=2)

        total_files = len(queue)

        while queue:
            src_file, dst_file = queue.popleft()
            dst_file.parent.mkdir(parents=True, exist_ok=True)
            self.input_path = src_file
            self.output_path = dst_file

            self.state = TransitionTarget.START
            self.round = 1

            self._run_fsm()

            with self.queue_path.open("w", encoding="utf-8") as f:
                json.dump([(str(s), str(d)) for s, d in queue], f, indent=2)

        self.queue_path.unlink(missing_ok=True)
        print(f"✅ All {total_files} file(s) processed")

    def _run_fsm(self):
        symbol = self.input_path.stem
        self.fsm_start_time = datetime.now(timezone.utc)
        print(f"🧠 Transforming: {symbol}")

        while self.state != TransitionTarget.END:
            print(f"🔁 Round {self.round} — State: {self.state.value.upper()}")
            try:
                result = self._execute_state(symbol)
            except Exception as e:
                self.error_logger.log(
                    experiment_id=self.config.experiment_id,
                    run_id=f"round-{self.round}-{symbol}",
                    round=self.round,
                    error_type="LLMExecutionError",
                    message=f"{str(e)}\nConfig: {self.config.model_dump_json(indent=2)}",
                    file_path=str(self.input_path)
                )
                return

            if result:
                self._post_process(result, symbol)

            self._evaluate_stopping_conditions(result)
            self._log_state(symbol, result)

            self.state_transition_logger.log(
                experiment_id=self.config.experiment_id,
                run_id=f"round-{self.round}-{symbol}",
                round=self.round,
                from_state=self.state.value.upper(),
                to_state=self.transition(self.state).value.upper(),
                reason="scored < threshold or max_iterations not reached"
            )

            self.state = self.transition(self.state)
            self.round += 1

        # Evaluate final result
        original_code = self.input_path.read_text(encoding="utf-8")
        modified_code = self.output_path.read_text(encoding="utf-8")
        score_data = self.evaluator.score(original_code, modified_code)

        # Determine outcome
        final_score = score_data["score"]
        passed = self.evaluator.meets_stopping_condition(score_data)
        reason_for_stop = (
            "threshold met"
            if passed else
            "max_iterations reached or failed to converge"
        )

        # Snapshot final evaluation
        self.snapshot_logger.log(
            round=self.round,
            symbol=symbol,
            original_code=original_code,
            modified_code=modified_code,
            diagnostics=score_data.get("metadata", {}),
            final_score=final_score,
            evaluator_name=score_data["evaluator_name"],
            evaluator_version=score_data["evaluator_version"],
            passed=passed,
            final=True
        )

        # Log experiment summary
        self.experiment_logger.log(
            experiment_id=self.config.experiment_id,
            description=self.config.description,
            mode=self.config.code_style.value,
            variant=self.config.generator.prompt_variant.value,
            max_iterations=int(self.config.generator.engine_config.get("max_iterations", 3)),
            stop_threshold=float(self.config.generator.engine_config.get("stop_threshold", 1.0)),
            model_engine=self.config.generator.engine.value,
            evaluator_name=score_data["evaluator_name"],
            evaluator_version=score_data["evaluator_version"],
            final_score=final_score,
            passed=passed,
            reason_for_stop=reason_for_stop,
            start=self.fsm_start_time,
            stop=datetime.now(timezone.utc)
        )

        elapsed = (datetime.now() - self.fsm_start_time).total_seconds()
        print(f"🛌 {symbol} complete after {self.round - 1} round(s) — {elapsed:.2f}s")

    def _execute_state(self, symbol: str) -> Optional[dict]:
        if self.state == TransitionTarget.START:
            # No agent runs during START; it just triggers the FSM to advance.
            return None

        input_payload = {
            "symbol": symbol,
            "file": str(self.input_path),
            "experiment_id": self.config.experiment_id,
            "run_id": f"round-{self.round}-{symbol}",
            "round": self.round,
            "system": self.config.system.value.upper(),  # ensure correct casing
            "log_path": self.log_dir
        }

        if self.state == TransitionTarget.GENERATOR:
            return self.generator.run(input_payload)

        elif self.state == TransitionTarget.DISCRIMINATOR:
            return self.discriminator.run(input_payload)

        elif self.state == TransitionTarget.MEDIATOR:
            return self.mediator.run(input_payload)

        elif self.state == TransitionTarget.PATCHOR:
            return self.patchor.run(input_payload)

        elif self.state == TransitionTarget.RECOMMENDER:
            return self.recommender.run(input_payload)

        return None

    def _post_process(self, result: dict, symbol: str):
        original_code = self.input_path.read_text(encoding="utf-8")
        modified_code = result.get("response", "")  # <- updated from .get("code")

        stripped, _ = strip_metadata_footer(modified_code)

        meta = FooterMetadata(
            system=self.config.system.value,
            experiment_id=self.config.experiment_id,
            run_id=f"round-{self.round}-{symbol}",
            file_path=str(self.input_path),
            date=datetime.now(timezone.utc),
            annotations_added=["docstring", "AI_HINT", "AI_LOG", "type_hints"],
            modifications=["refactor", "logging", "error_handling"],
            expected_tests="unit: 3, edge: 1, integration: 0"
        )
        full_code = append_metadata_footer(stripped, meta)
        self.output_path.write_text(full_code, encoding="utf-8")

        if self.evaluator:
            round_score = self.evaluator.score(original_code, full_code)
            self.snapshot_logger.log(
                round=self.round,
                symbol=symbol,
                original_code=original_code,
                modified_code=full_code,
                diagnostics=round_score.get("metadata", {}),
                final_score=round_score["score"],
                evaluator_name=round_score["evaluator_name"],
                evaluator_version=round_score["evaluator_version"],
                passed=self.evaluator.meets_stopping_condition(round_score)
            )
            self.state_logger.log(
                experiment_id=self.config.experiment_id,
                run_id=f"round-{self.round}-{symbol}",
                round=self.round,
                symbol=symbol,
                final=False,
                score=round_score["score"],
                passed=self.evaluator.meets_stopping_condition(round_score),
                evaluator_name=round_score["evaluator_name"],
                evaluator_version=round_score["evaluator_version"],
                diagnostics=round_score.get("metadata", {})
            )

            self.evaluation_logger.log(
                experiment_id=self.config.experiment_id,
                run_id=f"round-{self.round}-{symbol}",
                round=self.round,
                symbol=symbol,
                final=False,
                score=round_score["score"],
                passed=self.evaluator.meets_stopping_condition(round_score),
                evaluator_name=round_score["evaluator_name"],
                evaluator_version=round_score["evaluator_version"],
                diagnostics=round_score.get("metadata", {})
            )

    def _evaluate_stopping_conditions(self, result: Optional[dict]):
        score_value = result.get("score", 0.0) if result else 0.0
        max_iterations = int(self.config.generator.engine_config.get("max_iterations", 3))
        stop_threshold = float(self.config.generator.engine_config.get("stop_threshold", 1.0))

        if self.round >= max_iterations:
            self.state = TransitionTarget.END
            self.reason_for_stop = "max_iterations reached"
        elif score_value >= stop_threshold:
            self.state = TransitionTarget.END
            self.reason_for_stop = "threshold met"
        else:
            self.reason_for_stop = "continuing"
        

    def _log_state(self, symbol: str, result: Optional[dict]):
        self.score = result.get("score", {}) if result else {}
        self.state_logger.log(
            experiment_id=self.config.experiment_id,
            run_id=f"round-{self.round}-{symbol}",
            system="Preprocessing",
            round=self.round,
            state=self.state.value.upper(),
            action=f"{self.state.value.lower()} executed",
            score=self.score,
            details="generator success" if self.state == TransitionTarget.GENERATOR else ""
        )

    def transition(self, state: TransitionTarget) -> TransitionTarget:
        if state == TransitionTarget.START:
            return TransitionTarget.GENERATOR
        elif state == TransitionTarget.GENERATOR:
            return TransitionTarget.DISCRIMINATOR
        elif state == TransitionTarget.DISCRIMINATOR:
            return TransitionTarget.MEDIATOR
        elif state == TransitionTarget.MEDIATOR:
            return TransitionTarget.PATCHOR
        elif state == TransitionTarget.PATCHOR:
            return TransitionTarget.RECOMMENDER
        elif state == TransitionTarget.RECOMMENDER:
            return TransitionTarget.GENERATOR
        return TransitionTarget.END
