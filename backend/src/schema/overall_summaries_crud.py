import hashlib
import json
from typing import List, Optional

from sqlalchemy.orm import Session

from src.schema.overall_summaries import OverallSummary


def _hash_filenames(file_names: List[str]) -> str:
    sorted_names = sorted(file_names)
    key_str = "|".join(sorted_names)
    return hashlib.sha256(key_str.encode("utf-8")).hexdigest()


def add_overall_summary(
    db: Session, file_names: List[str], summary: str
) -> OverallSummary:
    pdf_set_hash = _hash_filenames(file_names)
    pdf_file_names_json = json.dumps(sorted(file_names))
    new_summary = OverallSummary(
        pdf_set_hash=pdf_set_hash, pdf_file_names=pdf_file_names_json, summary=summary
    )
    db.add(new_summary)
    db.commit()
    db.refresh(new_summary)
    return new_summary


def get_overall_summary(db: Session, file_names: List[str]) -> Optional[OverallSummary]:
    pdf_set_hash = _hash_filenames(file_names)
    return db.query(OverallSummary).filter_by(pdf_set_hash=pdf_set_hash).first()


def delete_overall_summary(db: Session, file_names: List[str]) -> bool:
    """Delete an overall summary for a set of filenames. Returns True if deleted."""
    pdf_set_hash = _hash_filenames(file_names)
    summary = db.query(OverallSummary).filter_by(pdf_set_hash=pdf_set_hash).first()
    if summary:
        db.delete(summary)
        db.commit()
        return True
    return False
