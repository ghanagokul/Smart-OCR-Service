import os
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import OperationalError

DB_URL = os.environ.get("DB_URL", "postgresql+psycopg2://ocr:ocr@db:5432/ocr")

# Retry loop for DB readiness
for i in range(10):
    try:
        engine = create_engine(DB_URL, pool_pre_ping=True)
        conn = engine.connect()
        conn.close()
        break
    except OperationalError:
        print(f"Database not ready yet... retrying ({i+1}/10)")
        time.sleep(3)
else:
    raise RuntimeError("Database connection failed after 10 retries")

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def get_session():
    return SessionLocal()
