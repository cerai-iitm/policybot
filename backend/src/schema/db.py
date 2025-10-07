import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

IN_DOCKER = os.getenv("IN_DOCKER", "0") == "1"
if IN_DOCKER:
    DB_HOST = "postgres_db"
else:
    DB_HOST = "localhost"

DATABASE_URL = f"postgresql+psycopg2://postgres:postgres@{DB_HOST}:5432/policybot"


engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
