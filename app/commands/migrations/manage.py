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
            if len(missing_tables) == 1:
                message = f"Add {missing_tables.pop()} table"
            else:
                message = f"Add {', '.join(sorted(missing_tables))} tables"
            click.echo(f"Using auto-generated message: {message}")
            
        # Create migration with the message
        try:
            # Create a new context for the create_migration command
            ctx = click.Context(create_migration)
            ctx.params = {'message': message}
            create_migration.invoke(ctx)
            
            click.echo("Migration created for missing tables")
            
            # Apply migrations if auto_apply is True
            if auto_apply:
                ctx = click.Context(apply_migrations)
                apply_migrations.invoke(ctx)
        except Exception as e:
            click.echo(f"Failed to create migration: {str(e)}", err=True)
    else:
        click.echo("No model changes detected")
        
        # If no tables are missing but auto_apply is True, still apply any pending migrations
        if auto_apply:
            click.echo("Checking for any pending migrations...")
            ctx = click.Context(apply_migrations)
            apply_migrations.invoke(ctx)