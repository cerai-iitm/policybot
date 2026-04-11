from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from db.base import Base


class PDF(Base):
    __tablename__ = "pdfs"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String(255), nullable=False, index=True)
    file_path = Column(String(500), nullable=False)
    notebook_id = Column(Integer, ForeignKey("notebooks.id"), nullable=False)
    processing_status = Column(String(50), default="uploaded")
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())

    notebook = relationship("Notebook", back_populates="pdfs")
