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
    export DATABASE_URL="postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}"
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

# Wait for PostgreSQL to be ready without requiring psql client
wait_for_postgres() {
    local host="$1"
    local port="$2"
    local max_attempts="$3"
    local timeout="$4"
    local attempt=0
    
    echo "Waiting for PostgreSQL to start at ${host}:${port}..."
    
    while [ $attempt -lt $max_attempts ]; do
        # Use netcat if available, otherwise try /dev/tcp bash builtin
        if command -v nc >/dev/null 2>&1; then
            nc -z -w $timeout $host $port >/dev/null 2>&1 && return 0
        else
            # Bash's /dev/tcp virtual device for tcp connections
            (echo > /dev/tcp/$host/$port) >/dev/null 2>&1 && return 0
        fi
        
        attempt=$((attempt+1))
        echo "PostgreSQL at ${host}:${port} is not available yet (Attempt $attempt/$max_attempts)..."
        sleep 3
    done
    
    return 1
}

# Wait for database to be ready
if ! wait_for_postgres "$POSTGRES_HOST" "$POSTGRES_PORT" 60 5; then
    echo "Error: Could not connect to PostgreSQL at ${POSTGRES_HOST}:${POSTGRES_PORT}"
    echo "Database connection details:"
    echo "  Host: $POSTGRES_HOST"
    echo "  Port: $POSTGRES_PORT"
    echo "  User: $POSTGRES_USER"
    echo "  Database: $POSTGRES_DB"
    exit 1
fi

echo "PostgreSQL is reachable. Starting Alembic migrations..."

# Use alembic directly for migrations
echo "Running database migrations..."
alembic upgrade head || {
    echo "Error: Failed to run migrations"
    echo "This could be because the database doesn't exist yet or isn't properly configured."
    echo "The application will still start, but some features may not work correctly."
}

# Initialize test data only in development
if [ "$ENVIRONMENT" != "production" ]; then
    echo "Initializing test data..."
    python init.py || echo "Warning: Test data initialization failed, but continuing"
fi

# Start the application
echo "Starting application..."
exec "$@" 