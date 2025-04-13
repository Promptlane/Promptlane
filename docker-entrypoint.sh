#!/bin/bash
set -e

# Create logs directory if it doesn't exist
mkdir -p logs

# Function to check required environment variables
check_required_vars() {
    local required_vars=("POSTGRES_USER" "POSTGRES_PASSWORD" "POSTGRES_DB" "POSTGRES_HOST")
    local missing_vars=()
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            missing_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -ne 0 ]; then
        echo "Error: Missing required environment variables: ${missing_vars[*]}"
        exit 1
    fi
}

# Check required variables
check_required_vars

# Set DATABASE_URL if not provided
if [ -z "$DATABASE_URL" ]; then
    export DATABASE_URL="postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT:-5432}/${POSTGRES_DB}"
    echo "Set DATABASE_URL to: $DATABASE_URL"
fi

# Check for SECRET_KEY in production
if [ "$ENVIRONMENT" = "production" ] && [ -z "$SECRET_KEY" ]; then
    echo "Error: SECRET_KEY is required in production environment"
    exit 1
fi

# Set default SECRET_KEY only in development
if [ "$ENVIRONMENT" != "production" ] && [ -z "$SECRET_KEY" ]; then
    export SECRET_KEY="default-secret-key-for-development-only"
    echo "WARNING: Using default SECRET_KEY for development only"
fi

# Install pydantic-settings if needed
python -c "import pydantic; v=pydantic.__version__; exit(0 if int(v.split('.')[0]) >= 2 else 1)" && \
    pip install --no-cache-dir pydantic-settings || \
    echo "Using Pydantic v1, no need for pydantic-settings"

# Set PYTHONPATH to include the app directory
export PYTHONPATH=/app

# Function to check if database is empty
check_database_empty() {
    # Check if alembic_version table exists
    if PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -U $POSTGRES_USER -d $POSTGRES_DB -tAc "SELECT 1 FROM information_schema.tables WHERE table_name='alembic_version'" | grep -q 1; then
        return 1  # Database is not empty
    else
        return 0  # Database is empty
    fi
}

# Function to check if initial migration exists
check_initial_migration() {
    if [ -f "alembic/versions/$(alembic history | grep -o '^[a-f0-9]*')_initial_migration.py" ]; then
        return 0
    else
        return 1
    fi
}

# Function to check if there are any pending model changes
check_pending_changes() {
    # Get current revision
    current_rev=$(alembic current)
    
    # Get head revision
    head_rev=$(alembic heads)
    
    # If current revision is not at head, there are pending changes
    if [ "$current_rev" != "$head_rev" ]; then
        return 0
    else
        return 1
    fi
}

# Function to check if there are any unapplied migrations
check_unapplied_migrations() {
    # Get current revision
    current_rev=$(alembic current)
    
    # Get head revision
    head_rev=$(alembic heads)
    
    # If current revision is not at head, there are unapplied migrations
    if [ "$current_rev" != "$head_rev" ]; then
        return 0
    else
        return 1
    fi
}

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to start..."
max_retries=30
count=0
until pg_isready -h $POSTGRES_HOST -p ${POSTGRES_PORT:-5432} -U $POSTGRES_USER -d $POSTGRES_DB || [ $count -eq $max_retries ]; do
    echo "Waiting for PostgreSQL to become available... ($count/$max_retries)"
    count=$((count+1))
    sleep 2
done

if [ $count -eq $max_retries ]; then
    echo "Error: Failed to connect to PostgreSQL after $max_retries attempts"
    exit 1
fi

echo "PostgreSQL is ready"

# Check if database is empty
if check_database_empty; then
    echo "Database is empty. Checking for existing migrations..."
    
    # If we have migrations but empty database, stamp the current revision
    if [ -d "alembic/versions" ] && [ "$(ls -A alembic/versions)" ]; then
        echo "Found existing migrations. Stamping current revision..."
        alembic stamp head || {
            echo "Error: Failed to stamp current revision"
            exit 1
        }
    else
        echo "No existing migrations found. Generating and applying initial migration..."
        
        # Generate initial migration
        alembic revision --autogenerate -m "initial migration" || {
            echo "Error: Failed to generate initial migration"
            exit 1
        }
        
        # Apply the initial migration
        alembic upgrade head || {
            echo "Error: Failed to apply initial migration"
            exit 1
        }
    fi
else
    echo "Database is not empty. Checking for migrations..."
    
    # Check for unapplied migrations
    if check_unapplied_migrations; then
        echo "Found unapplied migrations. Running migrations..."
        alembic upgrade head || {
            echo "Error: Failed to run migrations"
            exit 1
        }
    else
        echo "Database is up to date with all migrations"
    fi
    
    # Check for pending model changes
    if check_pending_changes; then
        echo "Detected model changes. Generating new migration..."
        alembic revision --autogenerate -m "model changes" || {
            echo "Error: Failed to generate migration for model changes"
            exit 1
        }
        
        # Apply the new migration
        echo "Applying new migration..."
        alembic upgrade head || {
            echo "Error: Failed to apply new migration"
            exit 1
        }
    fi
fi

# Initialize test data only in development
if [ "$ENVIRONMENT" != "production" ]; then
    echo "Initializing test data..."
    python init.py || echo "Warning: Test data initialization failed, but continuing"
fi

# Start the application
echo "Starting application..."
exec "$@" 