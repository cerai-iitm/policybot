from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship

from ..config import Base

from .notebooks import Notebook


class PDF(Base):
    __tablename__ = "pdfs"
    id = Column(Integer, primary_key=True)
    file_name = Column(String, nullable=False, index=True)
    file_path = Column(String, nullable=False)
    notebook_id = Column(Integer, ForeignKey("notebooks.id"), nullable=False)
    processing_status = Column(
        String, nullable=False, default="uploaded", server_default="uploaded"
    )
    uploaded_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    notebook = relationship("Notebook", back_populates="pdfs")

    # Unique constraint: file_name + notebook_id (file names unique per notebook)
    __table_args__ = (
        UniqueConstraint("file_name", "notebook_id", name="uix_pdf_filename_notebook"),
    )


# Add back reference to Notebook
Notebook.pdfs = relationship(
    "PDF", back_populates="notebook", cascade="all, delete-orphan"
)
