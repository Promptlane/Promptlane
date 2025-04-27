import click
from ..utils.tables import check_missing_tables

@click.command()
def check_migrations():
    """Check for missing database tables."""
    click.echo("Checking for missing database tables...")
    
    missing_tables = check_missing_tables()
    if missing_tables:
        click.echo(f"Missing tables detected: {', '.join(missing_tables)}")
    else:
        click.echo("All model tables exist in the database")
