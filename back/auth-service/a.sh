#!/bin/bash

# Wait for PostgreSQL to be ready
until pg_isready -h db -p 5432 -U db_user -d shared_db; do
  echo "Waiting for PostgreSQL to be ready..."
  sleep 2
done

cp /app/env.py /app/app/migrations/env.py

echo "PostgreSQL is ready, generating initial Alembic migration..."
# Generate initial migration
# ALEMBIC_ASYNC=1 alembic revision --autogenerate -m "Create auth tables"
alembic revision --autogenerate -m "Create auth tables"

echo "Running Alembic migrations..."
# Run Alembic migrations
# ALEMBIC_ASYNC=1 alembic upgrade head
alembic upgrade head

echo "Starting FastAPI application..."
# Start the FastAPI app
exec uvicorn app.main:app --host 0.0.0.0 --port 8000