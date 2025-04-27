import click
import alembic.config
from pathlib import Path

@click.command()
def show_migration_status():
    """Show the current migration status."""
    click.echo("Checking migration status...")
    
    alembic_ini_path = Path(__file__).parent.parent.parent.parent / "alembic.ini"
    if not alembic_ini_path.exists():
        click.echo(f"Alembic config file not found at {alembic_ini_path}", err=True)
        return False
    
    try:
        # Show current migration
        click.echo("\nCurrent migration:")
        current_args = [
            '-c', str(alembic_ini_path),
            'current'
        ]
        alembic.config.main(argv=current_args)
        
        # Show migration history
        click.echo("\nMigration history:")
        history_args = [
            '-c', str(alembic_ini_path),
            'history', '--indicate-current'
        ]
        alembic.config.main(argv=history_args)
        return True
    except Exception as e:
        click.echo(f"Error checking migration status: {str(e)}", err=True)
        return False
