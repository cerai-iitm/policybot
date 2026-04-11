#!/bin/sh
set -e

echo "Starting backend in ${APP_ENV:-production} mode"

# Wait for database to be ready using POSTGRES_* environment variables
DB_HOST="${POSTGRES_HOST:-postgres}"
DB_PORT="${POSTGRES_PORT:-5432}"

echo "Waiting for database at $DB_HOST:$DB_PORT..."
until nc -z "${DB_HOST}" "${DB_PORT}"; do
  echo "Postgres is unavailable at ${DB_HOST}:${DB_PORT} - sleeping"
  sleep 1
done
echo "Database is reachable"

# ---- Run migrations ----
if [ "${RUN_MIGRATIONS:-true}" = "true" ]; then
  echo "Running database migrations..."
  cd /app/backend && PYTHONPATH=/app alembic upgrade head
  echo "Migrations complete"
else
  echo "Skipping migrations (RUN_MIGRATIONS != true)"
fi

# ---- Exec CMD ----
echo "Starting application..."
exec "$@"
