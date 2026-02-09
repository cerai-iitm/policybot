"""
Database schema module.

Import all models here so Alembic autogenerate can detect them.
"""

from src.schema.db import Base
from src.schema.notebooks import Notebook
from src.schema.overall_summaries import OverallSummary
from src.schema.pdfs import PDF
from src.schema.source_summaries import SourceSummary

__all__ = ["Base", "Notebook", "PDF", "OverallSummary", "SourceSummary"]
