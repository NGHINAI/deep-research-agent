from sqlalchemy import create_engine, Column, String, DateTime, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import uuid

Base = declarative_base()

class ResearchDataDB(Base):
    __tablename__ = 'research_data'
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    source_url = Column(String)
    extracted_content = Column(String)
    credibility_score = Column(Float)
    freshness = Column(DateTime)
    topics = Column(JSON)

class ReportFragmentDB(Base):
    __tablename__ = 'content_fragments'
    section_id = Column(String, primary_key=True)
    content = Column(String)
    sources = Column(JSON)
    version_history = Column(JSON)

class SessionContextDB(Base):
    __tablename__ = 'session_context'
    session_id = Column(String, primary_key=True)
    research_state = Column(JSON)
    generation_progress = Column(JSON)
    validation_metrics = Column(JSON)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)

def init_db() -> scoped_session:
    engine = create_engine('sqlite:///research.db')
    Session = scoped_session(sessionmaker(bind=engine))
    
    try:
        Base.metadata.create_all(engine)
        logger.info('Database initialized successfully')
    except SQLAlchemyError as e:
        logger.error(f'Database initialization failed: {str(e)}')
        raise
    
    return Session

def safe_commit(session: scoped_session) -> bool:
    try:
        session.commit()
        return True
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f'Database commit failed: {str(e)}')
        return False
    return False