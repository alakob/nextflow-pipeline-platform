# Nextflow Pipeline Platform: Installation Guide

> 🗓️ **Last updated**: March 24, 2025

This guide provides detailed instructions for setting up the Nextflow Pipeline Platform in different environments.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Environment Setup Options](#environment-setup-options)
  - [Local Development Environment](#local-development-environment)
  - [Testing Environment](#testing-environment)
  - [Production Environment](#production-environment)
- [Basic Installation](#basic-installation)
- [Configuration](#configuration)
- [Environment-Specific Setup](#environment-specific-setup)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)

## Prerequisites

Before installing the Nextflow Pipeline Platform, ensure you have the following prerequisites:

- **Docker** and **Docker Compose** (v1.29.0+)
- **Python** (v3.9+)
- **Node.js** (v16+) and **npm** (v8+)
- **AWS CLI** (v2+) configured with appropriate credentials
- **Nextflow** (v23.04.0+)
- **Git** (v2.30+)
- **PostgreSQL** client tools (for database management)

## Environment Setup Options

The Nextflow Pipeline Platform can be deployed in multiple environments, each with its specific configuration.

### Local Development Environment

The development environment is used for active development and testing new features.

**Characteristics:**
- Fast iteration cycles
- Local database instance
- Simplified AWS configuration with localstack or direct AWS connections
- Features in development

### Testing Environment

The testing environment is used for integration testing and quality assurance.

**Characteristics:**
- Isolated from development and production
- Test database with test datasets
- Testing-specific AWS resources
- Stable features only

### Production Environment

The production environment is the live system used by end-users.

**Characteristics:**
- High availability setup
- Robust database configuration
- Production-grade AWS resources
- Stable, released features only
- Monitoring and alerting

## Basic Installation

Follow these steps to install the basic platform:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-org/nextflow-pipeline-platform.git
   cd nextflow-pipeline-platform
   ```

2. **Set up the backend**:
   ```bash
   # Create and activate a Python virtual environment
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Initialize the database (development environment)
   alembic upgrade head
   ```

3. **Set up the frontend**:
   ```bash
   cd ../frontend
   npm install
   ```

4. **Set up Docker services**:
   ```bash
   cd ..
   docker-compose up -d
   ```

## Configuration

### Environment Variables

Create appropriate `.env` files for different environments. Example configuration for development:

```bash
# .env.development
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/nextflow_db
TEST_DATABASE_URL=postgresql://user:password@localhost:5432/nextflow_test_db

# AWS Configuration
AWS_REGION=us-west-2
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
S3_BUCKET=nextflow-data-dev

# JWT Authentication
SECRET_KEY=your_secret_key_for_dev
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Nextflow Configuration
NEXTFLOW_EXECUTABLE=/path/to/nextflow
NEXTFLOW_WORK_DIR=/path/to/work
NEXTFLOW_BATCH_QUEUE=nextflow-batch-dev
```

Similar files should be created for testing (`.env.test`) and production (`.env.production`) with appropriate values.

### Database Setup

Initialize the database for each environment:

```bash
# Development
export ENV=development
alembic upgrade head

# Testing
export ENV=test
alembic upgrade head

# Production
export ENV=production
alembic upgrade head
```

## Environment-Specific Setup

### Development Environment

Additional development environment setup:

1. **Start the backend server in development mode**:
   ```bash
   cd backend
   source venv/bin/activate
   export ENV=development
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Start the frontend development server**:
   ```bash
   cd frontend
   npm run dev
   ```

3. **Local AWS resources setup**:
   ```bash
   # Using localstack (optional)
   docker run -d -p 4566:4566 -p 4571:4571 localstack/localstack
   
   # Configure AWS CLI to use localstack
   aws configure set aws_access_key_id test
   aws configure set aws_secret_access_key test
   aws configure set region us-west-2
   aws configure set endpoint_url http://localhost:4566
   
   # Create necessary resources
   aws --endpoint-url=http://localhost:4566 s3 mb s3://nextflow-data-dev
   ```

### Testing Environment

Setting up the testing environment:

1. **Configure testing environment**:
   ```bash
   export ENV=test
   ```

2. **Run the test suite**:
   ```bash
   cd backend
   source venv/bin/activate
   pytest
   
   cd ../frontend
   npm test
   ```

3. **Testing environment AWS resources**:
   
   Create a dedicated AWS account for testing or use resource prefixes to isolate testing resources.
   
   ```bash
   # Example: Create testing resources
   aws s3 mb s3://nextflow-data-test
   aws batch create-compute-environment --compute-environment-name nextflow-compute-test [...]
   aws batch create-job-queue --job-queue-name nextflow-batch-test [...]
   ```

### Production Environment

Setting up the production environment:

1. **Configure for production**:
   ```bash
   export ENV=production
   ```

2. **Set up production database**:
   Use a managed PostgreSQL service like AWS RDS for production:
   
   ```bash
   # Update the DATABASE_URL in .env.production to point to your RDS instance
   ```

3. **Production deployment**:
   
   Deploy the application using Docker:
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
   ```

4. **Set up AWS resources**:
   
   Ensure all AWS resources are properly configured for production:
   ```bash
   # Create production S3 bucket
   aws s3 mb s3://nextflow-data-prod
   
   # Set up Batch resources
   aws batch create-compute-environment --compute-environment-name nextflow-compute-prod [...]
   aws batch create-job-queue --job-queue-name nextflow-batch-prod [...]
   
   # Set up appropriate IAM roles and policies
   aws iam create-role --role-name nextflow-execution-role [...]
   ```

5. **Monitoring and logging setup**:
   ```bash
   # Set up CloudWatch for monitoring
   aws logs create-log-group --log-group-name /nextflow/pipeline/prod
   ```

## Verification

Verify your installation by running a test pipeline:

1. **Start the platform**:
   ```bash
   # In development mode
   cd backend
   source venv/bin/activate
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   
   # In a new terminal
   cd frontend
   npm run dev
   ```

2. **Open the web interface**:
   
   Navigate to http://localhost:3000 in your browser.

3. **Login and submit a test pipeline**:
   
   Use the sample pipeline provided in the `pipeline/examples` directory.

## Troubleshooting

### Common Issues

#### Database Connection Errors

If you encounter database connection issues:

1. Verify that PostgreSQL is running:
   ```bash
   docker ps | grep postgres
   ```

2. Check the database connection string in your `.env` file

3. Ensure the database exists:
   ```bash
   psql -U user -h localhost -p 5432 -l
   ```

#### AWS Configuration Issues

If you encounter AWS-related issues:

1. Verify AWS credentials:
   ```bash
   aws sts get-caller-identity
   ```

2. Check S3 bucket permissions:
   ```bash
   aws s3 ls s3://nextflow-data-dev/
   ```

3. Validate Batch compute environment:
   ```bash
   aws batch describe-compute-environments --compute-environments nextflow-compute-dev
   ```

#### Nextflow Execution Issues

If pipelines fail to execute:

1. Check Nextflow installation:
   ```bash
   nextflow -version
   ```

2. Verify that the Nextflow executable path is correctly set in your environment

3. Check the AWS Batch job queue and compute environment

### Getting Help

If you continue to experience issues, please:

1. Check the [Frequently Asked Questions](faq.md) document
2. Review the [Developer Guide](developer_guide.md) for more information
3. Open an issue in the project repository with detailed information about your problem

## Next Steps

After installation, follow the [Getting Started](getting_started.md) guide to learn how to use the platform.

**Related Documentation**:
- [Getting Started Guide](getting_started.md)
- [Developer Guide](developer_guide.md)
- [Architecture Diagram](architecture_diagram.md)
- [API Documentation](api.md)
- [Workflow Diagrams](workflow_diagrams.md)
