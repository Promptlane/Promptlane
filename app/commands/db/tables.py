import click
from sqlalchemy import inspect
from app.db.database import db
from app.db.models import Base

def get_model_tables():
    """Get all tables defined in the SQLAlchemy models"""
    return {table_name for table_name in Base.metadata.tables.keys()}

def get_database_tables(session):
    """Get all tables that exist in the database"""
    inspector = inspect(session.connection())
    return set(inspector.get_table_names())

@click.command()
def check_tables():
    """Check for missing database tables."""
    click.echo("Checking for missing database tables...")
    
    session = db.get_session()
    try:
        model_tables = get_model_tables()
        db_tables = get_database_tables(session)
        missing_tables = model_tables - db_tables
        
        if missing_tables:
            click.echo(f"Missing tables detected: {', '.join(missing_tables)}")
        else:
            click.echo("All model tables exist in the database")
    finally:
        db.close_session(session)

@click.command()
def list_tables():
    """List all tables in the database."""
    click.echo("Listing database tables...")
    
    session = db.get_session()
    try:
        db_tables = get_database_tables(session)
        if db_tables:
            click.echo("\nDatabase tables:")
            for table in sorted(db_tables):
                click.echo(f"  - {table}")
        else:
            click.echo("No tables found in the database")
    finally:
        db.close_session(session)

@click.command()
def seed_llm_models():
    """Seed the database with LLM models (OpenAI, Anthropic, etc.)."""
    from app.db.seed.llm_models.llm_models import seed
    seed()
    click.echo("LLM models seeded successfully.")
