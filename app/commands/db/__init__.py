import click
# from .init import init_db
# from .superuser import create_superuser
from .tables import check_tables, list_tables

@click.group()
def db_group():
    """Database management commands."""
    pass

# db_group.add_command(init_db)
# db_group.add_command(create_superuser)

db_group.add_command(check_tables, name='check-tables')
db_group.add_command(list_tables, name='list-tables')
