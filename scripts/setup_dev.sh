#!/bin/bash
# Nextflow Pipeline Platform Development Setup Script
# This script sets up a complete development environment for the Nextflow Pipeline Platform

set -e  # Exit on error

echo "🚀 Setting up Nextflow Pipeline Platform development environment..."

# Check prerequisites
echo "Checking prerequisites..."

command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3.10+ is required but not installed. Aborting."; exit 1; }
command -v node >/dev/null 2>&1 || { echo "❌ Node.js is required but not installed. Aborting."; exit 1; }
command -v psql >/dev/null 2>&1 || { echo "⚠️ PostgreSQL not found. You'll need to set up the database manually."; }
command -v docker >/dev/null 2>&1 || { echo "⚠️ Docker not found. It's recommended for local development."; }

# Get Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
if (( $(echo "$PYTHON_VERSION < 3.10" | bc -l) )); then
  echo "❌ Python 3.10+ is required. Found $PYTHON_VERSION. Aborting."
  exit 1
fi

# Create necessary directories
mkdir -p logs

# Set up the backend
echo "📦 Setting up backend..."
cd backend || { echo "❌ Backend directory not found. Aborting."; exit 1; }

# Create and activate virtual environment
if [ ! -d "venv" ]; then
  python3 -m venv venv
  echo "🔨 Created Python virtual environment"
fi

source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "🔨 Installing dependencies (this may take a few minutes)..."
# Main dependencies
pip install fastapi==0.115.11 sqlalchemy==2.0.39 alembic==1.15.1 psycopg2-binary==2.9.10
# AWS and Authentication
pip install boto3==1.37.18 pyjwt==2.10.1 python-jose[cryptography] passlib[bcrypt]
# Testing
pip install pytest==8.3.5 pytest-asyncio httpx

# Create env file if not exists
if [ ! -f ".env" ]; then
  cp .env.example .env
  echo "⚠️ Created .env file from template. Please update with your configuration before proceeding."
fi

# Set up the database if PostgreSQL is available
if command -v psql >/dev/null 2>&1; then
  echo "🛢️ Setting up PostgreSQL database..."
  if psql -lqt | cut -d \| -f 1 | grep -qw "nextflow_platform_dev"; then
    echo "✅ Database already exists. Skipping."
  else
    createdb nextflow_platform_dev || { echo "⚠️ Could not create database. You may need to create it manually."; }
  fi
else
  echo "⚠️ PostgreSQL not found. Please set up the database manually."
fi

# Run migrations if the database exists
if psql -lqt | cut -d \| -f 1 | grep -qw "nextflow_platform_dev"; then
  echo "🔨 Running database migrations..."
  alembic upgrade head
else
  echo "⚠️ Database not available. Skipping migrations."
fi

# Set up the frontend
echo "🖥️ Setting up frontend..."
cd ../frontend || { echo "❌ Frontend directory not found. Aborting."; exit 1; }

# Install dependencies
npm install

# Create env file if not exists
if [ ! -f ".env" ]; then
  cp .env.example .env
  echo "⚠️ Created .env file from template. Please update with your configuration before proceeding."
fi

# Return to the root directory
cd ..

# Set up pipeline directory
echo "🧬 Setting up Nextflow pipeline components..."
if [ ! -d "pipeline/nextflow" ]; then
  mkdir -p pipeline/nextflow
  mkdir -p pipeline/modules
  mkdir -p pipeline/conf
  echo "📁 Created pipeline directories"
fi

# Check if Terraform is installed
cd infra || { echo "❌ Infrastructure directory not found. Aborting."; exit 1; }
if command -v terraform >/dev/null 2>&1; then
  echo "🏗️ Terraform found. Initializing infrastructure modules..."
  terraform init
else
  echo "⚠️ Terraform not found. You'll need to install it for infrastructure management."
fi

# Return to the root directory
cd ..

echo "
✅ Setup complete!

To start the backend:
  cd backend
  source venv/bin/activate
  uvicorn app.main:app --reload

To start the frontend:
  cd frontend
  npm start

For more information, see the documentation in the docs/ directory.
"
