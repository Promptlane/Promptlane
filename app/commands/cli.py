"""
Promptlane Command Line Interface

This is the main entry point for all Promptlane commands.
"""

import click
from pathlib import Path
import sys

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

@click.group()
def cli():
    """Promptlane command line interface."""
    pass

# Import and register command groups
from .db import db_group
from .migrations import migrations_group
from .auth import auth_group

cli.add_command(db_group, name="db")
cli.add_command(migrations_group, name="migrations")
cli.add_command(auth_group, name="auth")

if __name__ == '__main__':
    cli()