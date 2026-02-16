from sqlalchemy import Column, String, Text, DateTime, func
from ..config import Base


class SuggestedQuestion(Base):
    __tablename__ = "suggested_questions"
    id = Column(String, primary_key=True)
    notebook_id = Column(String, nullable=False, index=True)
    filename = Column(String, nullable=True, index=True)
    question = Column(Text, nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
