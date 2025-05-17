from datetime import datetime
from pydantic import BaseModel


class FooterMetadata(BaseModel):
    system: str
    experiment_id: str
    run_id: str
    file_path: str
    date: datetime
    annotations_added: list[str]
    modifications: list[str]
    expected_tests: str
