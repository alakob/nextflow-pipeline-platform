provider "aws" {
  region = "eu-north-1"
  alias  = "main"
}

provider "aws" {
  region = "us-east-1"
  alias  = "us_east"
}

# S3 bucket for Nextflow data
data "aws_s3_bucket" "nextflow_data" {
  provider = aws.us_east
  bucket   = "nextflow-pipeline-data-${random_string.suffix.result}"
}

# Set S3 bucket ownership controls instead of ACL
resource "aws_s3_bucket_ownership_controls" "nextflow_data_ownership" {
  provider = aws.us_east
  bucket = data.aws_s3_bucket.nextflow_data.id
  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

# Random string for unique naming
resource "random_string" "suffix" {
  length  = 8
  special = false
  lower   = true
  upper   = false
}

# IAM role for AWS Batch
resource "aws_iam_role" "batch_role" {
  provider = aws.main
  name = "batch_service_role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = { Service = "batch.amazonaws.com" }
    }]
  })
}

# Attach policy to Batch role
resource "aws_iam_role_policy_attachment" "batch_policy" {
  provider   = aws.main
  role       = aws_iam_role.batch_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSBatchServiceRole"
}

# IAM role for EC2 instances in the batch environment
resource "aws_iam_role" "batch_instance_role" {
  provider = aws.main
  name = "batch_instance_role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = { Service = "ec2.amazonaws.com" }
    }]
  })
}

# Attach necessary policies to the instance role
resource "aws_iam_role_policy_attachment" "batch_instance_role_policy" {
  provider   = aws.main
  role       = aws_iam_role.batch_instance_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role_policy_attachment" "batch_s3_access" {
  provider   = aws.main
  role       = aws_iam_role.batch_instance_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"
}

resource "aws_iam_instance_profile" "batch_instance_profile" {
  provider = aws.main
  name = "batch_instance_profile"
  role = aws_iam_role.batch_instance_role.name
}

# Use existing VPC and subnet instead of creating new ones
# Reference to existing VPC
data "aws_vpc" "existing_vpc" {
  provider = aws.main
  id = "vpc-02bd5f585c2af6bc8"
}

# Reference to existing subnet
data "aws_subnet" "existing_subnet" {
  provider = aws.main
  id = "subnet-049b2ae5a41e5d1df"
}

# Reference to existing security group
data "aws_security_group" "existing_sg" {
  provider = aws.main
  id = "sg-054ac359718ae6efb"
}

# AWS Batch compute environment
resource "aws_batch_compute_environment" "nextflow_compute" {
  provider = aws.main
  compute_environment_name = "nextflow_compute"
  type                     = "MANAGED"
  
  compute_resources {
    max_vcpus     = 16
    min_vcpus     = 0
    type          = "EC2"
    instance_type = ["optimal"]
    
    security_group_ids = [data.aws_security_group.existing_sg.id]
    subnets            = [data.aws_subnet.existing_subnet.id]
    
    instance_role = aws_iam_instance_profile.batch_instance_profile.arn
  }
  
  service_role = aws_iam_role.batch_role.arn
}

# AWS Batch job queue
resource "aws_batch_job_queue" "nextflow_queue" {
  provider = aws.main
  name                 = "nextflow_queue"
  state                = "ENABLED"
  priority             = 1
  compute_environment_order {
    order = 0
    compute_environment = aws_batch_compute_environment.nextflow_compute.arn
  }
}

# AWS Batch job definition
resource "aws_batch_job_definition" "nextflow_job_def" {
  provider = aws.main
  name = "nextflow-job-definition"
  type = "container"
  
  container_properties = jsonencode({
    image      = "nfcore/rnaseq:latest"
    vcpus      = 2
    memory     = 4096
    command    = ["nextflow", "run", "main.nf", "--outdir", "s3://${data.aws_s3_bucket.nextflow_data.bucket}/results"]
    jobRoleArn = aws_iam_role.batch_instance_role.arn
    
    environment = [
      { name = "AWS_REGION", value = "eu-north-1" }
    ]
    
    mountPoints = [
      {
        containerPath = "/tmp"
        sourceVolume  = "tmp"
        readOnly      = false
      }
    ]
    
    volumes = [
      {
        name = "tmp"
        host = {
          sourcePath = "/tmp"
        }
      }
    ]
  })
}

# Variable for DB password (kept for future RDS setup)
variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}

# Outputs
output "s3_bucket_name" {
  description = "Name of the S3 bucket for Nextflow data"
  value       = data.aws_s3_bucket.nextflow_data.bucket
}

output "batch_job_queue_arn" {
  description = "ARN of the Batch job queue"
  value       = aws_batch_job_queue.nextflow_queue.arn
}