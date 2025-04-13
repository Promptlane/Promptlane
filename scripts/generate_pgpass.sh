#!/bin/bash

# Load environment variables if .env file exists
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi

# Generate pgpass file
echo "db:${POSTGRES_PORT:-5432}:postgres:${POSTGRES_USER:-postgres}:${POSTGRES_PASSWORD:-postgres}" > pgpass
echo "db:${POSTGRES_PORT:-5432}:${POSTGRES_DB:-promptlane}:${POSTGRES_USER:-postgres}:${POSTGRES_PASSWORD:-postgres}" >> pgpass

# Set proper permissions
chmod 600 pgpass

echo "pgpass file generated successfully." 