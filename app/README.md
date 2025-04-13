# PromptLane Application

This directory contains the core application code for PromptLane, a FastAPI-based application for managing prompts and projects.

## Project Structure

```
app/
├── config/            # Application configuration
│   ├── base.py       # Base configuration
│   ├── development.py # Development settings
│   ├── production.py # Production settings
│   ├── testing.py    # Testing settings
│   └── auth.py       # Authentication settings
├── db/               # Database configuration and models
│   ├── database.py   # Database connection
│   └── models/       # SQLAlchemy models
├── dependencies/     # FastAPI dependencies
├── managers/         # Business logic managers
├── middleware/       # Custom middleware
├── models/          # Pydantic models
├── routers/         # API routes and endpoints
├── services/        # Business logic services
├── static/          # Static files (CSS, JS, images)
├── templates/       # HTML templates
├── utils/           # Utility functions and helpers
├── error_handlers.py # Global error handling
├── exceptions.py    # Custom exceptions
├── logger.py        # Logging configuration
└── main.py          # Application entry point
```

## Configuration

The application uses a hierarchical configuration system:

### Environment Files

- `.env.example` - Template for environment variables
- `.env.development` - Development environment settings
- `.env.production` - Production environment settings

### Configuration Classes

- `base.py` - Base configuration with all settings
- `development.py` - Development-specific overrides
- `production.py` - Production-specific overrides
- `testing.py` - Testing-specific overrides

### Key Configuration Sections

1. **Database Settings**
   ```python
   POSTGRES_HOST=db
   POSTGRES_PORT=5432
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgres
   POSTGRES_DB=promptlane
   ```

2. **Security Settings**
   ```python
   JWT_SECRET_KEY=your-secret-key
   JWT_ALGORITHM=HS256
   JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

3. **API Settings**
   ```python
   API_V1_PREFIX=/api
   ALLOWED_ORIGINS=http://localhost:8000,http://localhost:3000
   ```

## Database Migrations

The application uses Alembic for database migrations:

### Migration Structure
```
alembic/
├── versions/         # Migration files
├── env.py           # Migration environment
├── script.py.mako   # Migration template
└── alembic.ini      # Alembic configuration
```

### Configuration Files

1. **alembic.ini.example**
   ```ini
   [alembic]
   script_location = alembic
   sqlalchemy.url = postgresql://%(POSTGRES_USER)s:%(POSTGRES_PASSWORD)s@%(POSTGRES_HOST)s:%(POSTGRES_PORT)s/%(POSTGRES_DB)s
   
   [loggers]
   keys = root,sqlalchemy,alembic
   
   [handlers]
   keys = console
   
   [formatters]
   keys = generic
   ```

2. **env.py**
   - Handles database connection
   - Configures migration context
   - Sets up logging
   - Imports SQLAlchemy models

### Migration Files

1. **Naming Convention**
   - Format: `{revision}_{description}.py`
   - Example: `a1b2c3d4_create_users_table.py`

2. **File Structure**
   ```python
   """create users table

   Revision ID: a1b2c3d4
   Revises: 
   Create Date: 2024-01-01 12:00:00.000000
   """
   
   from alembic import op
   import sqlalchemy as sa
   
   revision = 'a1b2c3d4'
   down_revision = None
   branch_labels = None
   depends_on = None
   
   def upgrade():
       op.create_table(
           'users',
           sa.Column('id', sa.Integer(), nullable=False),
           sa.Column('email', sa.String(), nullable=False),
           sa.PrimaryKeyConstraint('id')
       )
   
   def downgrade():
       op.drop_table('users')
   ```

### Common Commands

```bash
# Initialize Alembic (first time only)
alembic init alembic

# Create a new migration
alembic revision --autogenerate -m "description"

# Apply all pending migrations
alembic upgrade head

# Apply next migration
alembic upgrade +1

# Rollback last migration
alembic downgrade -1

# Rollback to specific version
alembic downgrade a1b2c3d4

# Show current revision
alembic current

# Show migration history
alembic history

# Show pending migrations
alembic history --indicate-current
```

### Best Practices

1. **Creating Migrations**
   - Always use `--autogenerate` for model changes
   - Review generated migration before applying
   - Test both upgrade and downgrade paths

2. **Version Control**
   - Commit migration files with model changes
   - Never modify existing migrations
   - Create new migration for schema changes

3. **Deployment**
   - Run migrations before application startup
   - Use transaction wrapping for safety
   - Backup database before major migrations

4. **Troubleshooting**
   - Check `alembic_version` table for current version
   - Verify database connection settings
   - Ensure all models are imported in `env.py`

## Authentication

The application uses JWT-based authentication:

1. **Protected Routes**
   - Defined in `config/auth.py`
   - Uses `AUTH_PROTECTED_PATHS` environment variable

2. **Public Routes**
   - Defined in `config/auth.py`
   - Uses `AUTH_PUBLIC_PATHS` environment variable

3. **Session Configuration**
   ```python
   SESSION_COOKIE_NAME=session
   SESSION_MAX_AGE=1800
   SESSION_SAME_SITE=lax
   SESSION_HTTPS_ONLY=false
   ```

## Development Setup

1. **Environment Setup**
   ```bash
   # Copy environment template
   cp .env.example .env.development

   # Update environment variables
   nano .env.development
   ```

2. **Database Setup**
   ```bash
   # Start database
   docker-compose up -d db

   # Run migrations
   alembic upgrade head
   ```

3. **Running the Application**
   ```bash
   # Development mode
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## Testing

1. **Environment Setup**
   ```bash
   # Copy environment template
   cp .env.example .env.testing

   # Update for testing
   nano .env.testing
   ```

2. **Running Tests**
   ```bash
   # Run all tests
   pytest

   # Run specific test
   pytest tests/test_file.py
   ```

## API Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Contributing

1. Create a new branch for your feature
2. Write tests for new functionality
3. Update documentation as needed
4. Submit a pull request

## License

[Your License Here] 