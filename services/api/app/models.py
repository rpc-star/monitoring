from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from datetime import datetime, timezone
from db import Base


class Result(Base):
    __tablename__ = "results"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    url = Column(String, nullable=False)
    status_code = Column(Integer, nullable=False)
    latency_ms = Column(Float, nullable=True)
    success = Column(Boolean, default=False)
    error = Column(String, nullable=True)
    