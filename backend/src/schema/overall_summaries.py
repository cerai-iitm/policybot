from sqlalchemy import Column, DateTime, Integer, String, Text, func

from src.schema.db import Base


class OverallSummary(Base):
    __tablename__ = "overall_summaries"
    id = Column(Integer, primary_key=True)
    pdf_set_hash = Column(String, unique=True, nullable=False, index=True)
    # Store filenames as a JSON string or structured text. Use Text to avoid length limits.
    pdf_file_names = Column(Text, nullable=False)
    # Summaries can be large — use Text instead of String to avoid default length limits.
    summary = Column(Text, nullable=False)
    # Use timezone-aware datetime for created_at
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
