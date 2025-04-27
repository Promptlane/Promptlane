"""
Promptlane management script.

Usage:
    python manage.py migrations check-tables
    python manage.py migrations create --message "Add new tables"
    python manage.py migrations apply
"""
import os
import sys

def main():
    """Run administrative tasks."""
    os.environ.setdefault('PYTHONPATH', os.path.dirname(os.path.abspath(__file__)))
    
    try:
        from app.commands.cli import cli
    except ImportError as exc:
        raise ImportError(
            "Couldn't import the CLI module. Are you sure it's installed?"
        ) from exc
    
    cli()

if __name__ == '__main__':
    main()
