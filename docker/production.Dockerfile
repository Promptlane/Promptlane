FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN apt-get update && \
    apt-get install -y postgresql-client && \
    pip install --no-cache-dir -r requirements/base.txt && \
    pip install --no-cache-dir -r requirements/production.txt

# Copy configuration files
COPY .env.example ./.env.example
COPY alembic.ini ./
COPY docker-entrypoint.sh ./

# Create necessary directories
RUN mkdir -p logs && \
    chmod +x docker-entrypoint.sh

# Copy only necessary files
COPY app/ ./app/
COPY alembic/ ./alembic/

EXPOSE 8000

ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 