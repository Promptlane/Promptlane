from sqlalchemy import inspect, text
from app.db.database import db
from app.db.models import Base

def get_model_tables():
    """Get all tables defined in the SQLAlchemy models"""
    return {table_name for table_name in Base.metadata.tables.keys()}

def get_database_tables(session):
    """Get all tables that exist in the database"""
    inspector = inspect(session.connection())
    return set(inspector.get_table_names())

def check_missing_tables():
    """Check for models that don't have corresponding tables in the database"""
    session = db.get_session()
    try:
        model_tables = get_model_tables()
        db_tables = get_database_tables(session)
        missing_tables = model_tables - db_tables
        return missing_tables
    finally:
        db.close_session(session)