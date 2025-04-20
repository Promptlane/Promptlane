from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import SQLAlchemyError, OperationalError, InterfaceError
import threading
import time
import logging
from typing import Optional, Generator
from contextlib import contextmanager
from app.config import settings
import os

# Configure logging
logger = logging.getLogger(__name__)

class Database:
    _instance = None
    _engine = None
    _SessionLocal = None
    _lock = threading.Lock()
    _connection_retries = settings.DATABASE.CONNECTION_RETRIES
    _retry_delay = settings.DATABASE.RETRY_DELAY  # seconds

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(Database, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if type(self)._engine is None:
            with self._lock:
                if type(self)._engine is None:
                    self._initialize_engine()

    def _initialize_engine(self):
        """Initialize the database engine with proper configuration and event handlers"""
        try:
            print(f"Attempting to connect to database at {settings.DATABASE.URL}")
            type(self)._engine = create_engine(
                str(settings.DATABASE.URL),
                poolclass=QueuePool,
                pool_pre_ping=settings.DATABASE.POOL_PRE_PING,
                pool_size=settings.DATABASE.POOL_SIZE,
                max_overflow=settings.DATABASE.MAX_OVERFLOW,
                pool_timeout=settings.DATABASE.POOL_TIMEOUT,
                pool_recycle=settings.DATABASE.POOL_RECYCLE,
                pool_use_lifo=settings.DATABASE.POOL_USE_LIFO,
                echo=settings.DATABASE.ECHO,
                echo_pool=settings.DATABASE.ECHO_POOL,
                connect_args={
                    'connect_timeout': settings.DATABASE.CONNECT_TIMEOUT,
                    'application_name': settings.APP.NAME
                }
            )

            # Configure session factory with scoped_session for thread safety
            type(self)._SessionLocal = scoped_session(
                sessionmaker(
                    autoflush=settings.DATABASE.SESSION_AUTOFLUSH,
                    bind=type(self)._engine,
                    expire_on_commit=settings.DATABASE.SESSION_EXPIRE_ON_COMMIT
                )
            )

            # Add event listeners
            self._setup_event_listeners()

            logger.info("Database engine initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database engine: {str(e)}")
            raise

    def _setup_event_listeners(self):
        """Setup SQLAlchemy event listeners for monitoring and error handling"""
        @event.listens_for(self._engine, "connect")
        def connect(dbapi_connection, connection_record):
            logger.debug("New database connection established")

        @event.listens_for(self._engine, "checkout")
        def checkout(dbapi_connection, connection_record, connection_proxy):
            cursor = dbapi_connection.cursor()
            try:
                cursor.execute("SELECT 1")
            except Exception:
                connection_proxy._pool.invalidate(dbapi_connection)
                raise
            finally:
                cursor.close()

        @event.listens_for(self._engine, "checkin")
        def checkin(dbapi_connection, connection_record):
            pass

        @event.listens_for(self._engine, "reset")
        def reset(dbapi_connection, connection_record):
            pass

    def get_session(self) -> Optional[scoped_session]:
        """Get a database session with retry mechanism"""
        for attempt in range(self._connection_retries):
            try:
                return self._SessionLocal()
            except (OperationalError, InterfaceError) as e:
                if attempt == self._connection_retries - 1:
                    logger.error(f"Failed to get database session after {self._connection_retries} attempts: {str(e)}")
                    raise
                logger.warning(f"Database connection attempt {attempt + 1} failed: {str(e)}")
                time.sleep(self._retry_delay)
        return None

    def close_session(self, session):
        """Safely close a database session"""
        try:
            if session:
                session.close()
        except Exception as e:
            logger.error(f"Error closing database session: {str(e)}")

    def shutdown(self):
        """Cleanup database resources"""
        try:
            if self._SessionLocal:
                self._SessionLocal.remove()
            if self._engine:
                self._engine.dispose()
            logger.info("Database resources cleaned up successfully")
        except Exception as e:
            logger.error(f"Error during database shutdown: {str(e)}")

    @property
    def engine(self):
        return self._engine

    @property
    def SessionLocal(self):
        return self._SessionLocal

# Create singleton instance
db = Database()

# Base class for SQLAlchemy models
Base = declarative_base()

# Dependency to get DB session with proper error handling
def get_db():
    session = None
    try:
        session = db.get_session()
        yield session
        session.commit()
    except SQLAlchemyError as e:
        if session:
            session.rollback()
        logger.error(f"Database error: {str(e)}")
        raise
    finally:
        if session:
            db.close_session(session)

@contextmanager
def session_scope() -> Generator:
    """Provide a transactional scope around a series of operations."""
    session = db.get_session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Transaction rolled back due to error: {str(e)}")
        raise
    finally:
        db.close_session(session)
