# Frequently Asked Questions (FAQ)

> ⏱️ **Time to read**: 10 minutes  
> 🗓️ **Last updated**: March 24, 2025

## Table of Contents

- [General Questions](#general-questions)
- [Installation & Setup](#installation--setup)
- [User Management](#user-management)
- [Pipeline Execution](#pipeline-execution)
- [AWS Integration](#aws-integration)
- [Troubleshooting](#troubleshooting)

## General Questions

<details>
<summary><strong>What is the Nextflow Pipeline Platform?</strong></summary>

The Nextflow Pipeline Platform is a web-based system for managing, executing, and monitoring bioinformatics pipelines built with the Nextflow workflow language. It provides a user-friendly interface for running complex computational pipelines on AWS infrastructure.
</details>

<details>
<summary><strong>What technologies does the platform use?</strong></summary>

The platform uses:
- **Backend**: Python with FastAPI, SQLAlchemy, and Alembic
- **Frontend**: React.js
- **Database**: PostgreSQL
- **Workflow Engine**: Nextflow
- **Cloud Infrastructure**: AWS (Batch, S3, EC2)
- **Infrastructure as Code**: Terraform
</details>

<details>
<summary><strong>Is the platform open source?</strong></summary>

Yes, the platform is released under the MIT license, which allows for both personal and commercial use with minimal restrictions.
</details>

## Installation & Setup

<details>
<summary><strong>What are the minimum system requirements?</strong></summary>

For local development:
- CPU: 2+ cores
- RAM: 4GB minimum, 8GB recommended
- Storage: 10GB free space
- Operating System: Linux, macOS, or Windows with WSL2

For production deployment:
- See the [Deployment Guide](./deployment.md) for AWS resource specifications
</details>

<details>
<summary><strong>How do I update to a newer version of the platform?</strong></summary>

1. Pull the latest changes:
   ```bash
   git pull origin main
   ```

2. Update dependencies:
   ```bash
   # Backend
   cd backend
   source venv/bin/activate
   pip install -r requirements.txt
   
   # Frontend
   cd ../frontend
   npm install
   ```

3. Run database migrations:
   ```bash
   cd backend
   alembic upgrade head
   ```
</details>

<details>
<summary><strong>Do I need AWS to run the platform?</strong></summary>

For development purposes, you can run the platform locally without AWS integration. However, to execute pipelines in production, you'll need an AWS account as the platform uses AWS Batch and S3 for scalable computation and storage.
</details>

## User Management

<details>
<summary><strong>How do I create an admin user?</strong></summary>

You can create an admin user either:

1. Through the database during initialization:
   ```bash
   cd backend
   python -m scripts.create_admin_user
   ```

2. By promoting an existing user to admin:
   ```bash
   cd backend
   python -m scripts.promote_to_admin --username your_username
   ```
</details>

<details>
<summary><strong>Can I integrate with existing authentication systems?</strong></summary>

Yes, the platform supports OAuth integration with providers like Google, GitHub, and OIDC-compliant identity providers. See the [Backend Development Guide](./backend_development.md#authentication-integration) for implementation details.
</details>

## Pipeline Execution

<details>
<summary><strong>How do I add a new pipeline to the platform?</strong></summary>

1. Upload your Nextflow pipeline to the `pipeline` directory
2. Register the pipeline through the admin interface
3. Configure the required parameters

For detailed instructions, see the [Pipeline Development Guide](./pipeline_development.md).
</details>

<details>
<summary><strong>What input data formats are supported?</strong></summary>

The platform supports any input data that your Nextflow pipeline can process. Common bioinformatics formats include:
- FASTQ files for sequencing data
- FASTA files for reference genomes
- BAM files for aligned sequences
- VCF files for variant data

All input data should be accessible via an S3 path.
</details>

<details>
<summary><strong>How do I monitor running pipelines?</strong></summary>

You can monitor running pipelines in several ways:
1. Through the web interface's Jobs Dashboard
2. Via the API endpoints for job status
3. Directly in AWS Batch console
4. Through CloudWatch logs

Each job provides real-time status updates and log access.
</details>

## AWS Integration

<details>
<summary><strong>What AWS permissions are required?</strong></summary>

The platform requires the following AWS permissions:
- S3: Read/Write access to your data buckets
- Batch: Full management of compute environments, job queues, and job definitions
- IAM: Ability to assume execution roles
- CloudWatch: Log group and metric creation/management

A detailed IAM policy template is available in the [Deployment Guide](./deployment.md#aws-permissions).
</details>

<details>
<summary><strong>How can I optimize AWS costs?</strong></summary>

To optimize costs:
1. Use Spot instances for non-critical workloads
2. Implement auto-scaling for compute environments
3. Set appropriate retention policies for S3 data
4. Configure proper instance types for your workloads
5. Use Resource Scheduling to run jobs during lower-cost periods

The platform includes built-in cost estimation and monitoring tools.
</details>

## Troubleshooting

<details>
<summary><strong>Pipeline jobs fail immediately</strong></summary>

Common causes:
1. Insufficient IAM permissions
2. Incorrect S3 paths for input data
3. Missing or incorrect AWS configuration

Solution:
1. Check the job logs in the platform interface
2. Verify AWS credentials and permissions
3. Validate that input data exists at the specified S3 paths
4. Ensure compute resources are correctly configured
</details>

<details>
<summary><strong>Backend fails to start</strong></summary>

Common causes:
1. Database connection issues
2. Missing environment variables
3. Port conflicts

Solution:
1. Verify PostgreSQL is running and accessible
2. Check that all required environment variables are set in `.env`
3. Ensure the configured port (default: 8000) is available
4. Check the logs for detailed error messages
</details>

<details>
<summary><strong>Frontend cannot connect to backend</strong></summary>

Common causes:
1. CORS configuration issues
2. Backend not running
3. Incorrect API URL in frontend configuration

Solution:
1. Verify the backend is running and accessible
2. Check the API URL in the frontend `.env` file
3. Ensure CORS settings in the backend allow connections from the frontend origin
</details>

## Additional Help

If you're experiencing issues not covered in this FAQ:

1. Check detailed logs in the backend and frontend
2. Search or create issues in the GitHub repository
3. Consult the platform documentation:
   - [User Guide](./user_guide.md)
   - [API Documentation](./api.md)
   - [Development Guide](./development.md)
   - [Deployment Guide](./deployment.md)
