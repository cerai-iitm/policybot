from src.schema.db import Base, engine
from src.schema.overall_summaries import OverallSummary
from src.schema.source_summaries import SourceSummary


def create_tables():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    create_tables()
