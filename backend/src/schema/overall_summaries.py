from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from src.schema.db import Base


class OverallSummary(Base):
    __tablename__ = "overall_summaries"
    id = Column(Integer, primary_key=True)
    pdf_set_hash = Column(String, unique=True, nullable=False, index=True)
    pdf_file_names = Column(
        String, nullable=False
    )  # Store as JSON string or comma-separated
    summary = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
