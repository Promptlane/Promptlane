#!/usr/bin/env python3
"""
Migration management script for Promptlane

This script provides an easy way to:
1. Check for missing database tables
2. Create migrations for new models or model changes
3. Apply pending migrations
4. Show migration status

Usage:
  python manage_migrations.py                # Check, create, and apply migrations
  python manage_migrations.py --check        # Only check for missing tables
  python manage_migrations.py --create       # Create migration if needed, don't apply
  python manage_migrations.py --apply        # Apply existing migrations
  python manage_migrations.py --status       # Show migration status
  python manage_migrations.py --message "Add new tables"   # Custom migration message
"""

import os
import sys
import logging
import argparse
from pathlib import Path
import alembic.config
from sqlalchemy import inspect, text

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("migration-manager")

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

# Import models after path setup
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
    logger.info("Checking for missing database tables...")
    session = db.get_session()
    try:
        # Get tables from models and database
        model_tables = get_model_tables()
        db_tables = get_database_tables(session)
        
        # Find tables that are in models but not in database
        missing_tables = model_tables - db_tables
        
        if missing_tables:
            logger.info(f"Missing tables detected: {', '.join(missing_tables)}")
            return True, list(missing_tables)
        else:
            logger.info("All model tables exist in the database")
            return False, []
    except Exception as e:
        logger.error(f"Error checking for missing tables: {str(e)}")
        return True, []  # Assume tables missing if there's an error
    finally:
        db.close_session(session)

def create_migration(message="Update database schema"):
    """Create a new migration based on model changes"""
    logger.info(f"Creating migration: {message}")
    
    alembic_ini_path = Path(__file__).parent / "alembic.ini"
    if not alembic_ini_path.exists():
        logger.error(f"Alembic config file not found at {alembic_ini_path}")
        return False
    
    try:
        alembic_args = [
            '-c', str(alembic_ini_path),
            'revision',
            '--autogenerate',
            '-m', message
        ]
        
        alembic.config.main(argv=alembic_args)
        logger.info("Migration file created successfully")
        return True
    except Exception as e:
        logger.error(f"Error creating migration: {str(e)}")
        return False

def apply_migrations():
    """Apply all pending migrations"""
    logger.info("Applying database migrations...")
    
    alembic_ini_path = Path(__file__).parent / "alembic.ini"
    if not alembic_ini_path.exists():
        logger.error(f"Alembic config file not found at {alembic_ini_path}")
        return False
    
    try:
        alembic_args = [
            '-c', str(alembic_ini_path),
            'upgrade', 'head'
        ]
        
        alembic.config.main(argv=alembic_args)
        logger.info("Migrations applied successfully")
        return True
    except Exception as e:
        logger.error(f"Error applying migrations: {str(e)}")
        return False

def show_migration_status():
    """Show the current migration status"""
    logger.info("Checking migration status...")
    
    alembic_ini_path = Path(__file__).parent / "alembic.ini"
    if not alembic_ini_path.exists():
        logger.error(f"Alembic config file not found at {alembic_ini_path}")
        return False
    
    try:
        alembic_args = [
            '-c', str(alembic_ini_path),
            'current'
        ]
        
        alembic.config.main(argv=alembic_args)
        
        # Also show pending migrations (history)
        logger.info("Pending migrations:")
        history_args = [
            '-c', str(alembic_ini_path),
            'history', '--indicate-current'
        ]
        
        alembic.config.main(argv=history_args)
        return True
    except Exception as e:
        logger.error(f"Error checking migration status: {str(e)}")
        return False

def manage_migrations(auto_apply=True, custom_message=None):
    """Check for missing tables and manage migrations"""
    tables_missing, missing_tables = check_missing_tables()
    
    if tables_missing:
        # Construct a meaningful message based on missing tables
        if missing_tables and not custom_message:
            message = f"Add {', '.join(missing_tables)} tables"
        else:
            message = custom_message or "Update database schema"
            
        # Create migration
        if create_migration(message):
            logger.info("Migration created for missing tables")
            
            # Apply migrations if auto_apply is True
            if auto_apply:
                if apply_migrations():
                    logger.info("Successfully applied migrations")
                    return True
                else:
                    logger.error("Failed to apply migrations")
                    return False
            return True
        else:
            logger.error("Failed to create migration")
            return False
    else:
        logger.info("No model changes detected")
        
        # If no tables are missing but auto_apply is True, still apply any pending migrations
        if auto_apply:
            logger.info("Checking for any pending migrations...")
            return apply_migrations()
        
        return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manage database migrations")
    parser.add_argument('--check', action='store_true', help='Check for missing tables only')
    parser.add_argument('--create', action='store_true', help='Create migration if needed')
    parser.add_argument('--apply', action='store_true', help='Apply pending migrations')
    parser.add_argument('--status', action='store_true', help='Show migration status')
    parser.add_argument('--message', type=str, default=None, help='Custom migration message')
    
    args = parser.parse_args()
    
    if args.check:
        check_missing_tables()
    elif args.create:
        tables_missing, _ = check_missing_tables()
        if tables_missing:
            create_migration(args.message or "Update database schema")
        else:
            logger.info("No model changes detected, no migration created")
    elif args.apply:
        apply_migrations()
    elif args.status:
        show_migration_status()
    else:
        # Default behavior: check, create and apply migrations
        manage_migrations(auto_apply=True, custom_message=args.message) 