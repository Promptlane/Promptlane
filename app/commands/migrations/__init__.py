import click
from .check import check_migrations
from .create import create_migration
from .apply import apply_migrations
from .status import show_migration_status
from .manage import manage_migrations

@click.group()
def migrations_group():
    """Database migration commands."""
    pass

# Add all commands with descriptive aliases
migrations_group.add_command(check_migrations, name='check-tables')
migrations_group.add_command(create_migration, name='create')
migrations_group.add_command(apply_migrations, name='apply')
migrations_group.add_command(show_migration_status, name='status')
migrations_group.add_command(manage_migrations, name='manage')