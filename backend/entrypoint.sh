#!/bin/bash
# filepath: /home/Gautam/Projects/cerai/policybot/backend/entrypoint.sh

# Wait for database to be ready
echo "Waiting for database..."
while ! nc -z postgres_db 5432; do
    sleep 1
done
echo "Database is ready!"

# Create tables
echo "Creating database tables..."
uv run python -m src.schema.create_tables

# Start the application
if [ "$MODE" = "prod" ]; then
    echo "Starting production server..."
    exec uv run uvicorn src.main:app --host 0.0.0.0 --port 8000
else
    echo "Starting development server..."
    exec uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
fi