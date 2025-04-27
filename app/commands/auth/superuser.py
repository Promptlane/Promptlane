import click
from getpass import getpass
from app.db.database import db
from app.db.models import User

@click.command()
@click.option('--username', prompt=True, help='Superuser username')
@click.option('--email', prompt=True, help='Superuser email')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='Superuser password')
def create_superuser(username, email, password):
    """Create a superuser account."""
    click.echo("Creating superuser...")
    
    session = db.get_session()
    try:
        # Check if user already exists
        existing_user = session.query(User).filter_by(email=email).first()
        if existing_user:
            click.echo(f"User with email {email} already exists", err=True)
            return False
        
        # Create new superuser
        user = User(
            username=username,
            email=email,
            is_superuser=True,
            is_active=True
        )
        user.set_password(password)
        
        session.add(user)
        session.commit()
        
        click.echo(f"Superuser {username} created successfully")
        return True
    except Exception as e:
        session.rollback()
        click.echo(f"Error creating superuser: {str(e)}", err=True)
        return False
    finally:
        db.close_session(session)
