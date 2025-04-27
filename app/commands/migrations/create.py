import click
import alembic.config
from pathlib import Path
from ..utils.tables import check_missing_tables
from .version import check_version_exists

@click.command()
@click.option('--message', '-m', help='Migration message')
def create_migration(message):
    """Create a new migration based on model changes."""
    click.echo("Creating migration...")
    
    alembic_ini_path = Path(__file__).parent.parent.parent.parent / "alembic.ini"
    if not alembic_ini_path.exists():
        click.echo(f"Alembic config file not found at {alembic_ini_path}", err=True)
        return False
    
    try:
        # Check if we need to apply existing migrations first
        version_exists = check_version_exists()
        if not version_exists:
            click.echo("Fresh database detected. Applying existing migrations first...")
            apply_args = [
                '-c', str(alembic_ini_path),
                'upgrade', 'head'
            ]
            alembic.config.main(argv=apply_args)
            click.echo("Existing migrations applied successfully")
        
        # Check if we need to create a new migration
        missing_tables = check_missing_tables()
        if not missing_tables:
            click.echo("No model changes detected, no new migration needed")
            return True
        
        # Create meaningful message if not provided
        if not message:
            message = f"Add {', '.join(missing_tables)} tables"
            
        # Create new migration
        alembic_args = [
            '-c', str(alembic_ini_path),
            'revision',
            '--autogenerate',
            '-m', message
        ]
        
        alembic.config.main(argv=alembic_args)
        click.echo("Migration file created successfully")
        return True
    except Exception as e:
        click.echo(f"Error creating migration: {str(e)}", err=True)
        return False
