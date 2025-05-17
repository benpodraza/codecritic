from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, Enum as SQLAlchemyEnum
from datetime import datetime, timezone
from core_microservice.app.enums.alert_enums import AlertTypeEnum, AlertScopeEnum, AlertSourceEnum

from core_microservice.app.db.base import Base

class AlertModel(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    alert_type = Column(SQLAlchemyEnum(AlertTypeEnum), nullable=False)
    alert_source = Column(SQLAlchemyEnum(AlertSourceEnum), nullable=False)
    alert_scope = Column(SQLAlchemyEnum(AlertScopeEnum), nullable=False)
    alert_payload = Column(JSON, nullable=False)
    alert_time = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    resolved = Column(Boolean, default=False, nullable=False)