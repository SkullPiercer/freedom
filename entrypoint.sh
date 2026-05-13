#!/bin/sh
set -e

if [ "${RUN_MIGRATIONS:-true}" = "true" ]; then
    echo "Running database migrations..."
    alembic upgrade head
else
    echo "Skipping database migrations..."
fi

echo "Starting application..."
exec "$@"
