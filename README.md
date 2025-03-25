# Nextflow Pipeline Platform

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.11-009688.svg)](https://fastapi.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A scalable platform for executing Nextflow pipelines on AWS with a FastAPI backend and React frontend.

<div align="center">
  <a href="./docs/assets/architecture_simple.md">System Architecture</a>
</div>

## 1. Overview

> ⏱️ **Time to read**: 5 minutes

The Nextflow Pipeline Platform provides a web-based interface for managing, executing, and monitoring bioinformatics pipelines built with the Nextflow framework. It leverages AWS infrastructure for scalable, cloud-based execution of compute-intensive pipelines.

**Key Features:**
- 🔐 User authentication with JWT
- 🧬 Pipeline management and versioning
- 🚀 Job submission with customizable parameters
- 📊 Real-time status monitoring and detailed job timeline
- 📥 Download functionality for completed analysis results
- ☁️ AWS infrastructure integration
- 🔄 RESTful API for programmatic access

For a detailed architecture overview, see [Architecture Documentation](./docs/architecture_diagram.md).

## 2. Quick Start Guide

### Prerequisites

- Python 3.10+
- Node.js 18+
- Docker and Docker Compose
- AWS Account with appropriate permissions

### Development Setup

The platform includes a comprehensive setup script that handles environment configuration and provides various options for starting services:

```bash
# Clone the repository
git clone https://github.com/alakob/nextflow-pipeline-platform.git
cd nextflow-pipeline-platform

# Run setup script (configures environment only)
./scripts/setup_dev.sh

# Start all services
./scripts/setup_dev.sh --start

# Start all services in detached mode (background)
./scripts/setup_dev.sh --start-detached

# Start only backend (with PostgreSQL)
./scripts/setup_dev.sh --start-backend

# Start only frontend
./scripts/setup_dev.sh --start-frontend

# Start backend in development mode with hot-reloading
./scripts/setup_dev.sh --start-backend-dev

# Start frontend in development mode
./scripts/setup_dev.sh --start-frontend-dev

# Run test suite
./scripts/setup_dev.sh --test
```

The setup script automatically:
- Configures a Docker-based PostgreSQL database
- Creates and activates Python virtual environment
- Installs all required dependencies
- Sets up environment variables
- Runs database migrations
- Prepares the frontend environment

### Manual Setup

If you prefer to set up components manually:

1. **Backend setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   cp .env.example .env      # Edit with your configuration
   alembic upgrade head      # Initialize database
   uvicorn app.main:app --reload
   ```

2. **Frontend setup**
   ```bash
   cd frontend
   npm install
   cp .env.example .env      # Edit with your configuration
   npm start
   ```

For more detailed setup instructions, see the [Development Guide](./docs/development.md).

## 3. Documentation

See the following documentation for more details:

- [Getting Started Guide](./docs/getting_started.md) - A step-by-step tutorial for new users
- [Developer Guide](./docs/developer_guide.md) - Architecture details and development guidelines
- [Workflow Diagrams](./docs/workflow_diagrams.md) - Visual representations of key platform processes
- [Installation Guide](./docs/installation_guide.md) - Multi-environment setup instructions
- [Frequently Asked Questions](./docs/faq.md) - Common questions and troubleshooting tips

## 4. Project Structure

```
/
├── backend/                # FastAPI Python backend
│   ├── app/                # API code
│   ├── db/                 # Database models
│   └── tests/              # Backend tests
├── frontend/               # React frontend
├── pipeline/               # Nextflow pipeline definitions
├── infra/                  # Terraform infrastructure code
└── docs/                   # Documentation
```

## 5. Development Workflow

The project includes comprehensive tooling to streamline the development process:

### Starting Services

```bash
# Start everything in one command
./scripts/setup_dev.sh --start

# View logs for specific service
docker-compose logs -f backend

# Stop all services
docker-compose down
```

### Database Operations

```bash
# Run database migrations
cd backend
source venv/bin/activate
alembic upgrade head

# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Reset database (interactive mode)
./backend/scripts/reset_db.sh dev

# Reset with sample data
./backend/scripts/reset_db.sh dev --with-sample-data

# Force reset without confirmation
./backend/scripts/reset_db.sh dev --force

# Reset test or production database
./backend/scripts/reset_db.sh test
./backend/scripts/reset_db.sh prod
```

### Testing

```bash
# Run all tests
./scripts/setup_dev.sh --test

# Backend tests only
cd backend
source venv/bin/activate
pytest

# Frontend tests
cd frontend
npm test
```

### Environment Management

- The application uses Docker Compose for consistent environments
- PostgreSQL runs in a container, eliminating the need for local installation
- All environment variables are configured in the `.env` file created by the setup script

### Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

See the [Development Guide](./docs/development.md) for coding standards and best practices.

## 6. Deployment

For production deployment on AWS:

1. Configure AWS credentials
2. Customize Terraform variables
3. Apply Terraform configuration
4. Deploy application components

Detailed instructions available in the [Deployment Guide](./docs/deployment.md).

## 7. License

This project is licensed under the MIT License - see the LICENSE file for details.

## 8. Project Status

This project is actively maintained. For roadmap information, see [Roadmap](./docs/roadmap.md).

## 9. FAQ

See the [Frequently Asked Questions](./docs/faq.md) document for common questions and troubleshooting tips.
