import click
from .superuser import create_superuser

@click.group()
def auth_group():
    """Authentication and authorization commands."""
    pass

auth_group.add_command(create_superuser, name='create-superuser')
