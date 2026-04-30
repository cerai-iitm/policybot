from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Boolean, func
from sqlalchemy.orm import relationship

from db.base import Base


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(50), unique=True, index=True, nullable=False)
    notebook_id = Column(Integer, ForeignKey("notebooks.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user = relationship("User", back_populates="chat_sessions")
    notebook = relationship("Notebook", back_populates="chat_sessions")
    chat_messages = relationship(
        "ChatMessage", back_populates="chat_session", cascade="all, delete-orphan"
    )
