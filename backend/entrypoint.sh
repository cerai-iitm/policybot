#!/bin/sh
set -e

echo "Starting backend in ${APP_ENV:-development} mode"

echo "DEBUG: DATABASE_URL is ${DATABASE_URL:+set and not empty}"

# ---- Wait for Postgres ----
# We use the DB_HOST variable you defined
if [ -n "$DB_HOST" ]; then
  echo "Waiting for database at $DB_HOST:$DB_PORT..."
  until nc -z "${DB_HOST}" "${DB_PORT:-5432}"; do
    echo "Postgres is unavailable - sleeping"
    sleep 1
  done
  echo "Database is reachable"
fi

# ---- Run migrations ----
echo "Attempting to run migrations..."
PYTHONPATH=/app alembic upgrade head

# ---- Exec CMD ----
echo "Starting application..."
exec "$@"
