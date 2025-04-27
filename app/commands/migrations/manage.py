import click
from ..utils.tables import check_missing_tables
from .create import create_migration
from .apply import apply_migrations

@click.command()
@click.option('--auto-apply/--no-auto-apply', default=True, help='Automatically apply migrations after creation')
@click.option('--message', '-m', help='Custom migration message')
def manage_migrations(auto_apply, message):
    """Check for missing tables and manage migrations."""
    click.echo("Managing migrations...")
    
    # Check for missing tables
    missing_tables = check_missing_tables()
    
    if missing_tables:
        # Construct a meaningful message based on missing tables
        if not message:
            message = f"Add {', '.join(missing_tables)} tables"
            
        # Create migration
        if create_migration(message):
            click.echo("Migration created for missing tables")
            
            # Apply migrations if auto_apply is True
            if auto_apply:
                if apply_migrations():
                    click.echo("Successfully applied migrations")
                else:
                    click.echo("Failed to apply migrations", err=True)
        else:
            click.echo("Failed to create migration", err=True)
    else:
        click.echo("No model changes detected")
        
        # If no tables are missing but auto_apply is True, still apply any pending migrations
        if auto_apply:
            click.echo("Checking for any pending migrations...")
            apply_migrations()
