from pathlib import Path
from app.enums.agent_management_enums import AgentRole
from app.schemas.experiment_config_schemas import ExperimentConfig
from app.utils.agent_factory.agent_factory import build_agent
from app.utils.runner.system_trainer import SystemTrainer

class PreprocessingTrainer(SystemTrainer):
    def __init__(
        self,
        experiment_path: Path,
        config: ExperimentConfig,
    ):

        super().__init__(
            experiment_path=experiment_path,
            config=config
        )
