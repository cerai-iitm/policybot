#!/bin/sh
set -e

echo "Starting backend in ${APP_ENV:-production} mode"

# Ensure proper permissions on mounted directories
# This handles cases where host directories are owned by root or different users
if [ -d "/app/backend/uploads" ]; then
    echo "Ensuring uploads directory permissions..."
    chmod 755 /app/backend/uploads 2>/dev/null || true
fi

if [ -d "/app/logs" ]; then
    echo "Ensuring logs directory permissions..."
    chmod 755 /app/logs 2>/dev/null || true
fi

# NOTE: Docker Compose already ensures PostgreSQL is healthy before this container starts
# The explicit nc‑based wait loop has been removed. The service will rely on the
# `depends_on` healthcheck defined in docker‑compose.yml. Migrations will still
# run once the container starts.


# ---- Run migrations ----
if [ "${RUN_MIGRATIONS:-true}" = "true" ]; then
    echo "Running database migrations..."
    # Alembic expects the `script_location` (migrations folder) relative to the cwd.
    # The migrations directory is at /app/migrations, so we run Alembic from the project root
    # and explicitly point it to the config file inside the backend package.
    cd /app && PYTHONPATH=/app alembic -c backend/alembic.ini upgrade head
    echo "Migrations complete"
else
    echo "Skipping migrations (RUN_MIGRATIONS != true)"
fi

# ---- Exec CMD ----
echo "Starting application..."
exec "$@"
