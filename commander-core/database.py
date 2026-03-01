import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

load_dotenv()

# 1. Fetch the Railway PostgreSQL URL, or fallback to local SQLite for dev
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./memory/sintari.db")

# 2. Fix Railway's "postgres://" driver string to "postgresql://" if necessary
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# 3. Create the SQLAlchemy Engine
# SQLite needs connect_args={"check_same_thread": False}, Postgres doesn't
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)

# 4. SessionLocal class factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 5. Base class for all models
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
