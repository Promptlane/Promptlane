#!/usr/bin/env python3
"""
This script creates the initial database migration.
Run this script after setting up the models to generate the initial migration.
"""
import os
import subprocess
import sys

def create_migration():
    """Create the initial migration"""
    try:
        # Check if alembic is installed
        subprocess.run(["alembic", "--version"], check=True, capture_output=True)
        
        # Create the initial migration
        result = subprocess.run(
            ["alembic", "revision", "--autogenerate", "-m", "Initial migration"],
            check=True,
            capture_output=True,
            text=True
        )
        
        print("Successfully created initial migration:")
        print(result.stdout)
        
    except subprocess.CalledProcessError as e:
        print(f"Error creating migration: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        sys.exit(1)
        
if __name__ == "__main__":
    create_migration() 