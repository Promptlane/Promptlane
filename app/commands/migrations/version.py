from sqlalchemy import text
from app.db.database import db

def check_version_exists():
    """Check if alembic_version table exists in the database"""
    session = db.get_session()
    try:
        session.execute(text("SELECT 1 FROM alembic_version LIMIT 1"))
        return True
    except:
        return False
    finally:
        db.close_session(session)
