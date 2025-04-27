# PromptLane

A modern platform for managing and versioning AI prompts, built with FastAPI.

## Table of Contents
- [Quick Start](#-quick-start)
- [Configuration](#-configuration)
- [Development](#-development)
- [Management Commands](#-management-commands)
- [Documentation](#-documentation)
- [Contributing](#-contributing)
- [License](#-license)

## 🚀 Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/promptlane/promptlane.git
   cd promptlane
   ```

2. Start the services:
   ```bash
   # For development environment (includes pgAdmin)
   docker compose --profile development up -d

   # For production environment
   docker compose --profile production up -d
   ```

3. Access the application:
   - API Documentation: `http://localhost:8000/docs`
   - Application: `http://localhost:8000`
   - pgAdmin (development only): `http://localhost:5050`

## ⚙️ Configuration

1. Copy environment template:
   ```bash
   cp .env.example .env
   ```

2. Configure environment variables:
   ```env
   # Database Configuration
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgres
   POSTGRES_DB=promptlane
   POSTGRES_HOST=db
   POSTGRES_PORT=5432

   # Security
   JWT_SECRET_KEY=your-secret-key
   SECRET_KEY=your-secret-key  # Required in production

   # Environment
   ENVIRONMENT=development  # or production
   ```

## 🔧 Development

### Starting Services
```bash
docker compose up -d
```

### Running Tests
```bash
docker compose exec app pytest
```

### Database Migrations
```bash
# Create new migration
docker compose --profile development exec app python manage.py migrations manage

# Create superuser
docker compose --profile development exec app python manage.py auth create-superuser
```

## 🛠️ Management Commands

All management commands are executed using `manage.py`:

### Database Migrations
```bash
# Check for missing tables
python manage.py migrations check-tables

# Create a new migration
python manage.py migrations create --message "Add new tables"

# Apply pending migrations
python manage.py migrations apply

# Show migration status
python manage.py migrations status

# Manage migrations (check, create, and apply)
python manage.py migrations manage
```

### Database Management
```bash
# Check for missing tables
python manage.py db check-tables

# List all tables in the database
python manage.py db list-tables
```

### Authentication
```bash
# Create superuser (interactive)
python manage.py auth create-superuser

# Create superuser (non-interactive)
python manage.py auth create-superuser \
  --username admin \
  --email admin@example.com \
  --password admin123
```

## 📚 Documentation

- **API Documentation**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **Swagger UI**: `http://localhost:8000/docs`

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">
  <sub>Built with ❤️ by the PromptLane team</sub>
</div>

