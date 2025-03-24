#!/bin/bash
# Nextflow Pipeline Platform Development Setup Script
# This script sets up a complete development environment for the Nextflow Pipeline Platform

# Important: Do not exit immediately on error for better error handling
# We will handle errors explicitly
set +e

echo "🚀 Setting up Nextflow Pipeline Platform development environment..."

# Check prerequisites
echo "Checking prerequisites..."

command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3.10+ is required but not installed. Aborting."; exit 1; }
command -v node >/dev/null 2>&1 || { echo "❌ Node.js is required but not installed. Aborting."; exit 1; }
command -v docker >/dev/null 2>&1 || { echo "❌ Docker is required but not installed. Aborting."; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "❌ Docker Compose is required but not installed. Aborting."; exit 1; }

# Get Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
if (( $(echo "$PYTHON_VERSION < 3.10" | bc -l) )); then
  echo "❌ Python 3.10+ is required. Found $PYTHON_VERSION. Aborting."
  exit 1
fi

# Create necessary directories
mkdir -p logs 2>/dev/null || true

# Function to wait for PostgreSQL to be ready
wait_for_postgres() {
  echo "⏳ Waiting for PostgreSQL to be ready..."
  local max_attempts=30
  local attempt=1

  while [ $attempt -le $max_attempts ]; do
    # First check if container is running
    if docker-compose ps | grep -q "postgres.*Up"; then
      # Then check if PostgreSQL is accepting connections
      if docker-compose exec -T postgres pg_isready -U postgres >/dev/null 2>&1; then
        echo "✅ PostgreSQL is ready"
        return 0
      fi
    else
      echo "⏳ PostgreSQL container is not yet running (attempt $attempt/$max_attempts)..."
    fi
    
    sleep 2
    ((attempt++))
  done

  echo "❌ PostgreSQL failed to become ready after $max_attempts attempts"
  return 1
}

# Setup backend environment
setup_backend() {
  echo "📦 Setting up backend..."
  cd backend || { echo "❌ Backend directory not found. Aborting."; exit 1; }

  # Create and activate virtual environment
  if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "🔨 Created Python virtual environment"
  fi

  source venv/bin/activate
  pip install --upgrade pip
  
  # Install from requirements.txt if it exists
  if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
  else
    echo "🔨 Installing dependencies (this may take a few minutes)..."
    # Main dependencies
    pip install fastapi==0.115.11 sqlalchemy==2.0.39 alembic==1.15.1 psycopg2-binary==2.9.10
    # AWS and Authentication
    pip install boto3==1.37.18 pyjwt==2.10.1 python-jose[cryptography] passlib[bcrypt]
    # Testing
    pip install pytest==8.3.5 pytest-asyncio httpx
  fi

  # Create env file if not exists
  if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
      cp .env.example .env
      echo "⚠️ Created .env file from template. Please update with your configuration before proceeding."
    else
      cat > .env << EOL
# Database configuration for Docker Compose
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/nextflow_platform

# Authentication
SECRET_KEY=local_development_secret_key_change_in_production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AWS Settings (for S3 storage)
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-west-2
S3_BUCKET=nextflow-data-local

# Environment
ENVIRONMENT=development

# Application settings
PORT=8000
LOG_LEVEL=INFO

# Testing
TESTING=false
EOL
      echo "⚠️ Created .env file. Please update with your configuration before proceeding."
    fi
  fi
  
  cd ..
  return 0
}

# Setup frontend environment
setup_frontend() {
  echo "🖥️ Setting up frontend..."
  cd frontend || { echo "❌ Frontend directory not found. Aborting."; exit 1; }

  # Install dependencies
  npm install

  # Create env file if not exists
  if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
      cp .env.example .env
      echo "⚠️ Created .env file from template. Please update with your configuration before proceeding."
    else
      cat > .env << EOL
# API endpoint URL
REACT_APP_API_URL=http://localhost:8000

# Environment
NODE_ENV=development

# Authentication settings
REACT_APP_AUTH_STORAGE_KEY=nextflow_auth_token
EOL
      echo "⚠️ Created .env file. Please update with your configuration before proceeding."
    fi
  fi
  
  cd ..
  return 0
}

# Setup pipeline environment
setup_pipeline() {
  echo "🧬 Setting up Nextflow pipeline components..."
  if [ ! -d "pipeline/nextflow" ]; then
    mkdir -p pipeline/nextflow 2>/dev/null || true
    mkdir -p pipeline/modules 2>/dev/null || true
    mkdir -p pipeline/conf 2>/dev/null || true
    echo "📁 Created pipeline directories"
  fi
  
  return 0
}

# Setup infrastructure
setup_infra() {
  if [ -d "infra" ]; then
    cd infra || return 0
    if command -v terraform >/dev/null 2>&1; then
      echo "🏗️ Terraform found. Initializing infrastructure modules..."
      terraform init
    else
      echo "⚠️ Terraform not found. You'll need to install it for infrastructure management."
    fi
    cd ..
  fi
  
  return 0
}

# Function to run database migrations after PostgreSQL is ready
run_migrations() {
  echo "🔨 Running database migrations..."
  cd backend || { echo "❌ Backend directory not found. Aborting migrations."; return 1; }
  source venv/bin/activate
  alembic upgrade head
  local migration_status=$?
  cd ..
  
  if [ $migration_status -eq 0 ]; then
    echo "✅ Migrations completed successfully."
  else
    echo "❌ Migration failed. Please check database connection and try again."
    return 1
  fi
  
  return 0
}

# Function to run tests
run_tests() {
  echo "🧪 Running tests..."
  cd backend || { echo "❌ Backend directory not found. Aborting tests."; return 1; }
  source venv/bin/activate
  python -m pytest
  local test_status=$?
  cd ..
  
  if [ $test_status -eq 0 ]; then
    echo "✅ All tests passed."
  else
    echo "❌ Some tests failed."
    return 1
  fi
  
  return 0
}

# Function to display usage instructions
display_usage() {
  echo ""
  echo "🚀 Nextflow Pipeline Platform setup complete!"
  echo ""
  echo "Available commands:"
  echo "  bash scripts/setup_dev.sh                       - Setup development environment only"
  echo "  bash scripts/setup_dev.sh --start               - Setup and start the full application stack"
  echo "  bash scripts/setup_dev.sh --start-backend       - Setup and start backend only"
  echo "  bash scripts/setup_dev.sh --start-frontend      - Setup and start frontend only"
  echo "  bash scripts/setup_dev.sh --start-detached      - Setup and start all services in detached mode"
  echo "  bash scripts/setup_dev.sh --start-backend-dev   - Start backend in development mode with hot reloading"
  echo "  bash scripts/setup_dev.sh --start-frontend-dev  - Start frontend in development mode with hot reloading"
  echo "  bash scripts/setup_dev.sh --test                - Run the test suite"
  echo ""
  echo "Manual commands:"
  echo "  docker-compose up                               - Start all services"
  echo "  docker-compose up -d                            - Start all services in detached mode"
  echo "  docker-compose logs -f [service]                - View logs for running services"
  echo "  docker-compose down                             - Stop all services"
  echo ""
}

# Main setup routine
setup_environment() {
  # Setup all components
  setup_backend
  setup_frontend
  setup_pipeline
  setup_infra
}

# Start services based on command-line argument
case "$1" in
  --start)
    # Setup environment first
    setup_environment
    
    echo "🚀 Starting the full application stack..."
    echo "📋 Press Ctrl+C to stop all services when done"
    
    # Make sure no services are running
    echo "🧹 Ensuring no services are running..."
    docker-compose down 2>/dev/null
    sleep 2 # Give time for services to fully stop
    
    # Build Docker images
    echo "🔨 Building Docker images..."
    docker-compose build
    
    # Start all services
    echo "🚀 Starting all services..."
    exec docker-compose up
    ;;
  --start-detached)
    # Setup environment first
    setup_environment
    
    echo "🚀 Starting all services in detached mode..."
    
    # Make sure no services are running
    echo "🧹 Ensuring no services are running..."
    docker-compose down 2>/dev/null
    sleep 2 # Give time for services to fully stop
    
    # Build Docker images
    echo "🔨 Building Docker images..."
    docker-compose build
    
    # Start all services in detached mode
    echo "🚀 Starting all services in detached mode..."
    if ! docker-compose up -d; then
      echo "❌ Failed to start services in detached mode."
      exit 1
    fi
    
    # Wait for PostgreSQL to be ready
    wait_for_postgres
    if [ $? -ne 0 ]; then
      echo "❌ PostgreSQL failed to start properly. Check Docker logs for details."
      exit 1
    fi
    
    # Run migrations if PostgreSQL is ready
    run_migrations
    
    echo "✅ Services started successfully in detached mode."
    echo "📋 View logs with: docker-compose logs -f"
    echo "📋 Stop services with: docker-compose down"
    
    # Check service health
    echo "📋 Service status:"
    docker-compose ps
    ;;
  --start-backend)
    # Setup environment first
    setup_environment
    
    echo "🚀 Starting the backend service with PostgreSQL..."
    
    # Stop any running backend services
    echo "🧹 Stopping any running backend services..."
    docker-compose stop postgres backend 2>/dev/null
    
    # Build backend image
    echo "🔨 Building Docker images..."
    docker-compose build backend
    
    # Start postgres and backend
    echo "🚀 Starting PostgreSQL and backend services..."
    exec docker-compose up postgres backend
    ;;
  --start-frontend)
    # Setup environment first
    setup_environment
    
    echo "🚀 Starting the frontend service..."
    
    # Stop any running frontend services
    echo "🧹 Stopping any running frontend services..."
    docker-compose stop frontend 2>/dev/null
    
    # Build frontend image
    echo "🔨 Building Docker images..."
    docker-compose build frontend
    
    # Start frontend
    echo "🚀 Starting frontend service..."
    exec docker-compose up frontend
    ;;
  --start-backend-dev)
    # Setup environment first
    setup_environment
    
    # Start postgres in detached mode
    echo "🚀 Starting PostgreSQL in detached mode..."
    
    # Make sure postgres is running
    if ! docker-compose ps | grep -q "postgres.*Up"; then
      echo "🚀 Starting PostgreSQL container..."
      if ! docker-compose up -d postgres; then
        echo "❌ Failed to start PostgreSQL in detached mode."
        exit 1
      fi
      
      # Wait for PostgreSQL to be ready
      wait_for_postgres
      if [ $? -ne 0 ]; then
        echo "❌ PostgreSQL failed to start properly. Check Docker logs for details."
        exit 1
      fi
      
      # Run migrations
      run_migrations
    else
      echo "✅ PostgreSQL is already running."
    fi
    
    # Start backend in development mode
    cd backend || { echo "❌ Failed to navigate to backend directory."; exit 1; }
    source venv/bin/activate
    echo "🚀 Starting backend in development mode..."
    echo "📋 Press Ctrl+C to stop the backend when done"
    exec uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    ;;
  --start-frontend-dev)
    # Setup environment first
    setup_environment
    
    cd frontend || { echo "❌ Failed to navigate to frontend directory."; exit 1; }
    echo "🚀 Starting frontend in development mode..."
    echo "📋 Press Ctrl+C to stop the frontend when done"
    exec npm start
    ;;
  --test)
    # Setup environment first
    setup_environment
    
    # Start postgres in detached mode if not already running
    echo "🚀 Ensuring PostgreSQL is running for tests..."
    if ! docker-compose ps | grep -q "postgres.*Up"; then
      echo "Starting PostgreSQL container..."
      if ! docker-compose up -d postgres; then
        echo "❌ Failed to start PostgreSQL for tests."
        exit 1
      fi
      
      # Wait for PostgreSQL to be ready
      wait_for_postgres
      if [ $? -ne 0 ]; then
        echo "❌ PostgreSQL failed to start properly. Check Docker logs for details."
        exit 1
      fi
    else
      echo "✅ PostgreSQL is already running."
    fi
    
    # Run tests
    run_tests
    ;;
  *)
    # Just setup the environment and display usage instructions if no arguments provided
    setup_environment
    display_usage
    ;;
esac

exit 0
