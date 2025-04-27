import click
import alembic.config
from pathlib import Path

@click.command()
def apply_migrations():
    """Apply pending migrations."""
    click.echo("Applying migrations...")
    
    alembic_ini_path = Path(__file__).parent.parent.parent.parent / "alembic.ini"
    if not alembic_ini_path.exists():
        click.echo(f"Alembic config file not found at {alembic_ini_path}", err=True)
        return False
    
    try:
        alembic_args = [
            '-c', str(alembic_ini_path),
            'upgrade', 'head'
        ]
        alembic.config.main(argv=alembic_args)
        click.echo("Migrations applied successfully")
        return True
    except Exception as e:
        click.echo(f"Error applying migrations: {str(e)}", err=True)
        return False
