#!/bin/sh
set -e

# Only the API container should run migrations; workers reuse this image and opt out.
if [ "${RUN_MIGRATIONS:-true}" = "true" ]; then
    echo "Running database migrations..."
    alembic upgrade head
else
    echo "Skipping database migrations..."
fi

echo "Starting application..."
exec "$@"
