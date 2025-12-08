from sqlalchemy.orm import Session

from src.schema.source_summaries import SourceSummary


def add_source_summary(db: Session, source_name: str, summary: str):
    new_summary = SourceSummary(source_name=source_name, summary=summary)
    db.add(new_summary)
    db.commit()
    db.refresh(new_summary)
    return new_summary


def delete_source_summary(db: Session, source_name: str):
    summary = (
        db.query(SourceSummary).filter(SourceSummary.source_name == source_name).first()
    )
    if summary:
        db.delete(summary)
        db.commit()
        return summary
    return None


def get_summary_by_source_name(db: Session, file_name: str):
    summary_obj = (
        db.query(SourceSummary).filter(SourceSummary.source_name == file_name).first()
    )
    if summary_obj:
        return str(summary_obj.summary)
    return None


def get_all_source_summaries(db: Session):
    return db.query(SourceSummary).all()
