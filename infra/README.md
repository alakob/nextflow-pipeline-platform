# Nextflow Pipeline Platform Infrastructure

This directory contains Terraform configurations for setting up the AWS infrastructure required for the Nextflow Pipeline Platform.

## Components

The infrastructure includes:

- **S3 Bucket**: For storing Nextflow pipeline data and results
- **AWS Batch**: For running Nextflow pipelines
  - Compute Environment
  - Job Queue
  - Job Definition with nf-core/rnaseq container
- **RDS PostgreSQL**: Database for the application
- **IAM Roles**: For AWS Batch service and EC2 instance permissions

## Usage

1. Install Terraform (version >= 1.0.0)
2. Update `terraform.tfvars` with your secure database password
3. Initialize Terraform:
   ```
   terraform init
   ```
4. Plan the infrastructure:
   ```
   terraform plan
   ```
5. Apply the configuration:
   ```
   terraform validate
   terraform apply
   ```
6. To destroy the infrastructure when no longer needed:
   ```
   terraform destroy
   ```

## Security Considerations

- The `terraform.tfvars` file contains sensitive information and should not be committed to version control
- Security group and subnet IDs should be updated to match your VPC configuration
- Consider using AWS Secrets Manager for managing the database password in production
- Update the S3 bucket policy and RDS security settings for production environments

## Connection to FastAPI Backend

Once the infrastructure is deployed, update the FastAPI backend environment variables:

```
DATABASE_URL=postgresql://admin:<password>@<rds_endpoint>/nextflow_db
AWS_S3_BUCKET=<s3_bucket_name>
AWS_BATCH_JOB_QUEUE=<batch_job_queue_arn>
AWS_BATCH_JOB_DEFINITION=<batch_job_definition_name>
```

These values can be obtained from Terraform outputs after applying the configuration.
