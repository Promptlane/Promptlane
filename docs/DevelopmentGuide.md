# PromptLane Development Guide

A guide for developers contributing to or customizing PromptLane.

## 🚀 Quick Setup

```bash
# Clone repository
git clone https://github.com/promptlane/promptlane.git
cd promptlane

# Copy environment files
cp .env.example .env
cp alembic.ini.example alembic.ini

# Build and start services
docker compose up --build -d

# Check service status
docker compose ps

# Run migrations
docker compose exec app alembic upgrade head
```

## 🐳 Docker Development

### Services Overview
```yaml
services:
  app:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./app:/app
    depends_on:
      - db
    environment:
      - POSTGRES_HOST=db
      - DEBUG=true

  db:
    image: postgres:15-alpine
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  pgadmin:
    image: dpage/pgadmin4
    ports:
      - "5050:80"
```

### Service URLs
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- PgAdmin: http://localhost:5050

## 📁 Project Structure

```
promptlane/
├── app/                 # Main application
│   ├── config/         # Configuration settings
│   ├── db/            # Database models
│   ├── dependencies/  # FastAPI dependencies
│   ├── managers/      # Business logic managers
│   ├── middleware/    # Custom middleware
│   ├── models/        # Pydantic models
│   ├── routers/       # API endpoints
│   ├── services/      # Business logic services
│   ├── static/        # Static assets
│   ├── templates/     # HTML templates
│   ├── utils/         # Utility functions
│   ├── error_handlers.py # Global error handling
│   ├── exceptions.py  # Custom exceptions
│   ├── logger.py      # Logging configuration
│   └── main.py        # Application entry point
├── alembic/           # Database migrations
├── docker/            # Docker configuration
├── docs/             # Documentation
├── logs/             # Application logs
├── requirements/      # Dependencies by environment
├── scripts/          # Utility scripts
├── tests/            # Test suite
├── .env.example      # Environment template
├── alembic.ini       # Alembic configuration
├── docker-compose.yml # Docker services
└── docker-entrypoint.sh # Container entry point
```

## 💻 Development Workflow

### Docker Commands
```bash
# Service management
docker compose up -d         # Start services
docker compose down         # Stop services
docker compose restart      # Restart services
docker compose ps          # Check status

# Logs
docker compose logs -f app  # Follow app logs
docker compose logs -f db   # Follow database logs

# Execute commands
docker compose exec app pytest                    # Run tests
docker compose exec app black .                   # Format code
docker compose exec app alembic upgrade head      # Run migrations

# Database
docker compose exec db psql -U postgres -d promptlane  # Access database
```

### Environment Variables
```env
# PostgreSQL
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=promptlane
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Application
DEBUG=true
SECRET_KEY=your-secret-key
ENVIRONMENT=development
```

## 🔧 Common Tasks

### Database Operations
```bash
# Backup database
docker compose exec db pg_dump -U postgres promptlane > backup.sql

# Restore database
docker compose exec -T db psql -U postgres promptlane < backup.sql

# Create migration
docker compose exec app alembic revision --autogenerate -m "description"

# Apply migration
docker compose exec app alembic upgrade head
```

### Container Management
```bash
# Rebuild specific service
docker compose up -d --build app

# View container logs
docker compose logs -f app

# Access container shell
docker compose exec app /bin/bash

# Clean up
docker compose down         # Stop containers
docker compose down -v      # Stop and remove volumes
docker compose down --rmi all  # Remove all containers and images
```

## 🔍 Debugging

1. Check logs:
   ```bash
   docker compose logs -f app
   ```

2. Common issues:
   - Database connection: Check DATABASE_URL and credentials
   - Import errors: Verify virtual environment and dependencies
   - Migration errors: Try recreating migrations

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Follow code style guidelines
4. Add tests for new features
5. Submit pull request

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [Docker Documentation](https://docs.docker.com/) 