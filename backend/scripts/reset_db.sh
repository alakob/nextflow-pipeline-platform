#!/bin/bash
# Database Reset Shell Script
# Makes resetting the database easier, especially in Docker environments

# Exit immediately if a command exits with non-zero status
set -e

# Default environment is development
ENV=${1:-dev}

echo "🔄 Resetting $ENV database..."

if [ "$ENV" = "prod" ]; then
  echo "⚠️  WARNING: You are about to reset the PRODUCTION database!"
  read -p "Are you absolutely sure? This cannot be undone! [y/N]: " confirm
  if [[ "$confirm" != [yY]* ]]; then
    echo "❌ Reset canceled."
    exit 1
  fi
fi

# Set database URL based on environment
if [ "$ENV" = "dev" ]; then
  export DATABASE_URL="postgresql+asyncpg://postgres:postgres@db:5432/nextflow_platform"
elif [ "$ENV" = "test" ]; then
  export DATABASE_URL="postgresql+asyncpg://postgres:postgres@db:5432/nextflow_platform_test"
elif [ "$ENV" = "prod" ]; then
  export DATABASE_URL="postgresql+asyncpg://postgres:postgres@db:5432/nextflow_platform_prod"
else
  echo "❌ Invalid environment: $ENV. Use 'dev', 'test', or 'prod'."
  exit 1
fi

# Determine whether to run directly or in Docker
if [ -f /.dockerenv ] || [ -f /run/.containerenv ]; then
  # We're inside a container, run directly
  echo "🐳 Running inside Docker container..."
  python scripts/reset_db.py "$@"
else
  # We're on the host, run in the backend container
  echo "🐳 Running in backend Docker container..."
  docker exec nextflow-pipeline-platform-backend-1 python scripts/reset_db.py "$@"
fi

echo "✅ Reset complete for $ENV environment."
