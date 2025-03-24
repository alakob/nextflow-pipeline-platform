# Deployment Guide for Nextflow Pipeline Platform

This document outlines the steps to deploy the Nextflow Pipeline Platform to AWS using Terraform for infrastructure provisioning.

## Prerequisites

- AWS account with appropriate permissions
- Terraform 1.5.0+
- Docker
- AWS CLI configured
- GitHub repository access

## Environment Setup

### 1. Configure AWS Credentials

Configure AWS credentials locally or in your CI/CD environment using one of these methods:

```bash
# Option 1: Configure using AWS CLI
aws configure

# Option 2: Set environment variables
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_REGION="us-west-2"
```

### 2. Repository Structure

Ensure your repository is organized as follows:
```
nextflow-pipeline-platform/
├── backend/                # FastAPI application
├── frontend/               # React frontend
├── infra/                  # Terraform files
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
├── pipeline/               # Nextflow pipeline configurations
└── .github/workflows/      # CI/CD configuration
```

## Terraform Infrastructure

### 1. Infrastructure Components

The Terraform configuration deploys:

- VPC with public and private subnets
- RDS PostgreSQL database
- ECR repositories for container images
- ECS Fargate services for the FastAPI application
- AWS Batch compute environment for Nextflow
- S3 buckets for pipeline input/output
- IAM roles and policies

### 2. Local Deployment

To deploy from your local machine:

```bash
cd infra/
terraform init
terraform plan
terraform apply
```

### 3. Infrastructure Variables

Key Terraform variables to configure:

| Variable | Description | Default |
|----------|-------------|---------|
| `aws_region` | AWS region for deployment | `us-west-2` |
| `environment` | Deployment environment (dev, test, prod) | `dev` |
| `db_instance_class` | RDS instance type | `db.t3.micro` |
| `vpc_cidr` | CIDR block for the VPC | `10.0.0.0/16` |

## Application Deployment

### 1. Docker Image Building

The CI/CD pipeline automatically builds and pushes Docker images to ECR.

Manual build steps:
```bash
cd backend/
docker build -t nextflow-platform-api:latest .
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REPOSITORY_URI
docker tag nextflow-platform-api:latest $ECR_REPOSITORY_URI:latest
docker push $ECR_REPOSITORY_URI:latest
```

### 2. Database Migrations

```bash
# Connect to an environment with database access (e.g., container shell)
cd backend/
alembic upgrade head
```

### 3. Environment Variables

Required environment variables for the application:

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `SECRET_KEY` | JWT secret key |
| `AWS_REGION` | AWS region (e.g., `us-west-2`) |
| `S3_BUCKET` | S3 bucket for pipeline data |
| `BATCH_QUEUE` | AWS Batch job queue ARN |
| `BATCH_JOB_DEFINITION` | AWS Batch job definition ARN |

## CI/CD Pipeline

The GitHub Actions workflow handles:
1. Testing the code
2. Building and pushing Docker images
3. Deploying infrastructure through Terraform
4. Applying database migrations

### Manual Deployment Steps

In case you need to deploy manually:

1. Run the tests locally to ensure everything works:
   ```bash
   cd backend/
   python -m pytest
   ```

2. Build and push Docker images:
   ```bash
   docker build -t nextflow-platform-api:latest ./backend/
   docker tag nextflow-platform-api:latest $ECR_REPOSITORY_URI:latest
   docker push $ECR_REPOSITORY_URI:latest
   ```

3. Apply Terraform infrastructure:
   ```bash
   cd infra/
   terraform apply
   ```

4. Update ECS services to use the new image:
   ```bash
   aws ecs update-service --cluster $CLUSTER_NAME --service $SERVICE_NAME --force-new-deployment
   ```

## Monitoring and Logging

- CloudWatch is configured to collect logs from the application
- Metrics for API and database performance are available in CloudWatch
- Set up CloudWatch alarms for critical metrics (API errors, high CPU/memory)

## Rollback Procedure

In case of deployment issues:

1. Identify the previous stable deployment version
2. Update the ECS service to use the previous image version:
   ```bash
   aws ecs update-service --cluster $CLUSTER_NAME --service $SERVICE_NAME --task-definition $PREVIOUS_TASK_DEFINITION
   ```

3. If infrastructure changes need to be rolled back:
   ```bash
   cd infra/
   terraform plan -target=module.ecs -out=rollback.plan
   terraform apply rollback.plan
   ```

## Security Considerations

- Database credentials are managed through AWS Secrets Manager
- API access is controlled through JWT authentication
- VPC endpoints are used to access AWS services securely
- Security groups restrict traffic to required ports only

## Next Steps

After deployment, verify the following:
1. API health check endpoint responds properly
2. Database migrations have been applied successfully
3. User creation and authentication work as expected
4. Pipeline job submission and monitoring are functional
