from sqlalchemy import Column, DateTime, ForeignKey, String, Text, func

from ..config import Base


class SuggestedQuestionExample(Base):
    __tablename__ = "suggested_question_examples"
    id = Column(String, primary_key=True)
    suggested_question_id = Column(
        String, ForeignKey("suggested_questions.id"), nullable=False, index=True
    )
    example_answer = Column(Text, nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
