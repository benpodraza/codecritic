from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, Enum as SQLAlchemyEnum
from datetime import datetime, timezone
from core_microservice.app.enums.alert_enums import AlertTypeEnum, AlertScopeEnum, AlertSourceEnum
from core_microservice.app.db.base import Base

class AlertModel(Base):
    """
    SQLAlchemy model for the 'alerts' table, representing alert records in the database.

    Attributes:
        id (int): Primary key for the alert record.
        alert_type (AlertTypeEnum): Type of the alert, defined by AlertTypeEnum.
        alert_source (AlertSourceEnum): Source of the alert, defined by AlertSourceEnum.
        alert_scope (AlertScopeEnum): Scope of the alert, defined by AlertScopeEnum.
        alert_payload (JSON): JSON payload containing alert-specific data.
        alert_time (datetime): Timestamp of when the alert was created, defaults to current UTC time.
        resolved (bool): Boolean flag indicating if the alert has been resolved, defaults to False.
    """
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    alert_type = Column(SQLAlchemyEnum(AlertTypeEnum), nullable=False)
    alert_source = Column(SQLAlchemyEnum(AlertSourceEnum), nullable=False)
    alert_scope = Column(SQLAlchemyEnum(AlertScopeEnum), nullable=False)
    alert_payload = Column(JSON, nullable=False)
    alert_time = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    resolved = Column(Boolean, default=False, nullable=False)

# === AI-FIRST METADATA ===
# source_file: C:\Repos\codecritic\experiments\experiment_1\inputs\alert_model.py
# agent: SelfRefinementAgent
# date: 2025-05-14T20:32:20.864210+00:00
# annotations_added: ['docstring', 'AI_HINT', 'AI_LOG', 'type_hints']
# modifications: ['refactor', 'logging', 'error_handling']
# expected_tests: unit: 3, edge: 1, integration: 0
