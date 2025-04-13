#!/bin/bash

# Load environment variables if .env file exists
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi

# Generate pgAdmin server configuration file
cat > pgadmin-servers.json << EOF
{
  "Servers": {
    "1": {
      "Name": "${APP_NAME:-Promptlane}",
      "Group": "Servers",
      "Host": "db",
      "Port": ${POSTGRES_PORT:-5432},
      "MaintenanceDB": "postgres",
      "Username": "${POSTGRES_USER:-postgres}",
      "SSLMode": "prefer",
      "PassFile": "/pgpass"
    }
  }
}
EOF

echo "pgAdmin server configuration file generated successfully." 