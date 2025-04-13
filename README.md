# PromptLane

A modern platform for managing and versioning AI prompts, built with FastAPI.

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/promptlane/promptlane.git
cd promptlane

# Start with Docker
docker compose up -d

# Run migrations
docker compose exec app alembic upgrade head
```

Visit `http://localhost:8000/docs` for API documentation.

## ⚙️ Configuration

1. Copy environment template:
   ```bash
   cp .env.example .env
   ```

2. Update required variables:
   ```env
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgres
   POSTGRES_DB=promptlane
   JWT_SECRET_KEY=your-secret-key
   ```

## 🔧 Development

```bash
# Start services
docker compose up -d

# Create migration
docker compose exec app alembic revision --autogenerate -m "description"

# Run tests
docker compose exec app pytest
```

## 📚 Documentation

- API Docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Submit pull request

## 📄 License

MIT License - See [LICENSE](LICENSE) for details. 