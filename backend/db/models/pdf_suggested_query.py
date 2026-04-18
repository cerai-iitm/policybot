# db/models/pdf_suggested_query.py
from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text, func
from sqlalchemy.orm import relationship

from db.base import Base


class PDFSuggestedQuery(Base):
    __tablename__ = "pdf_suggested_queries"

    id = Column(Integer, primary_key=True, index=True)
    pdf_id = Column(
        Integer,
        ForeignKey("pdfs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    query_text = Column(Text, nullable=False)
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    pdf = relationship("PDF", back_populates="suggested_queries")
