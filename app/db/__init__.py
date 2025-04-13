"""
Database package for Promptlane.
"""
# Import and expose models
from .models import Base, User, Team, TeamMember, Project, Prompt, Activity, ActivityType, TeamRole


# Import and expose utility functions
from .util import serialize_details, UUIDEncoder

# Import database singleton
from .database import db

# Import database initialization functions
from .init_db import init_database, create_admin_user

# This file indicates that the directory is a Python package 