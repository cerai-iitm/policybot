from sqlalchemy import Column, DateTime, Integer, String, Text, func

from src.schema.db import Base


class Notebook(Base):
    __tablename__ = "notebooks"
    id = Column(Integer, primary_key=True)
    notebook_id = Column(String, unique=True, nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
