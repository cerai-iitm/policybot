from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from db.base import Base


class PDF(Base):
    __tablename__ = "pdfs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    notebook_id = Column(Integer, ForeignKey("notebooks.id"), nullable=False)

    original_filename = Column(String(255), nullable=False)
    stored_filename = Column(String(44), nullable=False, unique=True)
    file_path = Column(String(500), nullable=False)

    processing_status = Column(String(50), default="uploaded")
    summary = Column(Text, nullable=True)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())

    notebook = relationship("Notebook", back_populates="pdfs")
    user = relationship("User")
