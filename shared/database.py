"""
Database schema for the TDS Project.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from shared.config import settings

Base = declarative_base()


class Task(Base):
    """Tasks sent to students."""
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    email = Column(String, nullable=False, index=True)
    task = Column(String, nullable=False, index=True)
    round = Column(Integer, nullable=False)
    nonce = Column(String, nullable=False, unique=True)
    brief = Column(Text, nullable=False)
    attachments = Column(Text)  # JSON string
    checks = Column(Text)  # JSON string
    evaluation_url = Column(String, nullable=False)
    endpoint = Column(String, nullable=False)
    statuscode = Column(Integer)
    secret = Column(String, nullable=False)


class Repo(Base):
    """Repository submissions from students."""
    __tablename__ = "repos"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    email = Column(String, nullable=False, index=True)
    task = Column(String, nullable=False, index=True)
    round = Column(Integer, nullable=False)
    nonce = Column(String, nullable=False)
    repo_url = Column(String, nullable=False)
    commit_sha = Column(String, nullable=False)
    pages_url = Column(String, nullable=False)


class Result(Base):
    """Evaluation results."""
    __tablename__ = "results"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    email = Column(String, nullable=False, index=True)
    task = Column(String, nullable=False, index=True)
    round = Column(Integer, nullable=False)
    repo_url = Column(String, nullable=False)
    commit_sha = Column(String, nullable=False)
    pages_url = Column(String, nullable=False)
    check = Column(String, nullable=False)
    score = Column(Float, nullable=False)
    reason = Column(Text)
    logs = Column(Text)


# Database setup
engine = create_engine(settings.database_url, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
