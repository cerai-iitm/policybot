from sqlalchemy import Column, Integer, String

from .db import Base


class SourceSummary(Base):
    __tablename__ = "source_summaries"
    id = Column(Integer, primary_key=True, index=True)
    source_name = Column(String, unique=True, index=True, nullable=False)
    summary = Column(String, nullable=False)
