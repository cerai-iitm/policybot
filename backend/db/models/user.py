from sqlalchemy import Column, DateTime, Integer, String, func
from sqlalchemy.orm import relationship

from db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(String, default="true")

    notebooks = relationship(
        "Notebook", back_populates="user", cascade="all, delete-orphan"
    )
    pdfs = relationship("PDF", back_populates="user", cascade="all, delete-orphan")
    chat_messages = relationship(
        "ChatMessage", back_populates="user", cascade="all, delete-orphan"
    )
