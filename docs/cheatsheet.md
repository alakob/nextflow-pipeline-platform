# Nextflow Pipeline Platform Cheat Sheet

> 📝 A quick reference guide for common tasks and commands

## Quick Navigation

- [Authentication](#authentication)
- [Pipeline Management](#pipeline-management)
- [Job Operations](#job-operations)
- [AWS Commands](#aws-commands)
- [Troubleshooting](#troubleshooting)
- [API Examples](#api-examples)

## Authentication

### Register a New User
```bash
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{"username": "new_user", "password": "secure_password"}'
```

### Login and Get Token
```bash
curl -X POST http://localhost:8000/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'
```

### Check Current User
```bash
curl -X GET http://localhost:8000/users/me \
  -H "Authorization: Bearer your_token_here"
```

## Pipeline Management

### List All Pipelines
```bash
curl -X GET http://localhost:8000/pipelines \
  -H "Authorization: Bearer your_token_here"
```

### Get Specific Pipeline
```bash
curl -X GET http://localhost:8000/pipelines/{pipeline_id} \
  -H "Authorization: Bearer your_token_here"
```

### Pipeline Parameters Quick Reference

| Common Parameter | Description | Example |
|------------------|-------------|---------|
| `reads` | Input sequence files | `s3://bucket/reads/*.fastq` |
| `genome` | Reference genome | `s3://bucket/ref/hg38.fa` |
| `max_cpus` | CPU cores per process | `4` |
| `max_memory` | Memory per process | `16.GB` |
| `outdir` | Results directory | `s3://bucket/results` |
| `resume` | Resume failed run | `true` |

## Job Operations

### Submit a Job
```bash
curl -X POST http://localhost:8000/pipelines/jobs \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_token_here" \
  -d '{
    "pipeline_id": "pipeline_id_here",
    "params": {
      "reads": "s3://bucket/reads/*.fastq",
      "genome": "s3://bucket/reference/hg38.fa"
    }
  }'
```

### List All Jobs
```bash
curl -X GET http://localhost:8000/pipelines/jobs \
  -H "Authorization: Bearer your_token_here"
```

### Get Job Status
```bash
curl -X GET http://localhost:8000/pipelines/jobs/{job_id} \
  -H "Authorization: Bearer your_token_here"
```

### Cancel a Job
```bash
curl -X DELETE http://localhost:8000/pipelines/jobs/{job_id} \
  -H "Authorization: Bearer your_token_here"
```

### Job Status Codes

| Status Code | Description |
|-------------|-------------|
| `QUEUED` | Job is waiting for resources |
| `PREPARING` | Setting up execution environment |
| `RUNNING` | Job is actively running |
| `COMPLETED` | Job finished successfully |
| `FAILED` | Job terminated with errors |
| `CANCELLED` | Job was manually stopped |

## AWS Commands

### Configure AWS Credentials
```bash
aws configure
# Enter your AWS Access Key ID, Secret Access Key, region, and output format
```

### Upload Data to S3
```bash
aws s3 cp /local/path/to/data s3://bucket-name/path/
```

### Download Results from S3
```bash
aws s3 cp s3://bucket-name/results/ /local/path/ --recursive
```

### Check S3 Bucket Contents
```bash
aws s3 ls s3://bucket-name/
```

### Create an S3 Bucket
```bash
aws s3 mb s3://new-bucket-name
```

### Check AWS Batch Job Status
```bash
aws batch describe-jobs --jobs job-id
```

## Troubleshooting

### Common Error Codes

| HTTP Code | Description | Common Cause |
|-----------|-------------|--------------|
| 400 | Bad Request | Missing required parameters |
| 401 | Unauthorized | Invalid or expired token |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 500 | Server Error | Backend failure |

### Common Job Failures

| Error Message | Likely Cause | Solution |
|---------------|--------------|----------|
| "Invalid S3 path" | Incorrect S3 URL format | Check S3 path syntax |
| "Access denied to S3" | Insufficient AWS permissions | Check IAM roles and policies |
| "Out of memory" | Process required more memory | Increase max_memory parameter |
| "Process timeout" | Long-running process terminated | Increase timeout or optimize pipeline |
| "Missing input file" | Input file not found | Verify input file existence and permissions |

### Fixing AWS Permissions

If you encounter permissions issues:

1. Verify AWS credentials are configured correctly
2. Check your IAM user has appropriate policies:
   - AmazonS3ReadOnlyAccess (minimum)
   - AmazonS3FullAccess (for write operations)
   - AmazonBatchFullAccess (for job management)

Example IAM policy for pipeline execution:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::input-bucket",
        "arn:aws:s3:::input-bucket/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::output-bucket",
        "arn:aws:s3:::output-bucket/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "batch:SubmitJob",
        "batch:DescribeJobs",
        "batch:TerminateJob"
      ],
      "Resource": "*"
    }
  ]
}
```

## API Examples

### Complete Workflow

```bash
# 1. Authenticate
TOKEN=$(curl -s -X POST http://localhost:8000/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}' \
  | jq -r '.access_token')

# 2. List available pipelines
curl -s -X GET http://localhost:8000/pipelines \
  -H "Authorization: Bearer $TOKEN" \
  | jq .

# 3. Get pipeline details
PIPELINE_ID="your_pipeline_id"
curl -s -X GET http://localhost:8000/pipelines/$PIPELINE_ID \
  -H "Authorization: Bearer $TOKEN" \
  | jq .

# 4. Submit a job
JOB_ID=$(curl -s -X POST http://localhost:8000/pipelines/jobs \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{
    \"pipeline_id\": \"$PIPELINE_ID\",
    \"params\": {
      \"reads\": \"s3://bucket/reads/*.fastq\",
      \"genome\": \"s3://bucket/reference/hg38.fa\"
    }
  }" | jq -r '.id')

# 5. Monitor job status
curl -s -X GET http://localhost:8000/pipelines/jobs/$JOB_ID \
  -H "Authorization: Bearer $TOKEN" \
  | jq .
```

### Asynchronous Job Completion Notification

1. Register a webhook:
```bash
curl -X POST http://localhost:8000/webhooks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "url": "https://your-service.com/webhook",
    "events": ["job.completed", "job.failed"]
  }'
```

2. Set up a simple webhook receiver (Python example):
```python
from fastapi import FastAPI, Request
import httpx

app = FastAPI()

@app.post("/webhook")
async def webhook_receiver(request: Request):
    data = await request.json()
    job_id = data["job_id"]
    status = data["status"]
    
    if status == "COMPLETED":
        # Download results, send notifications, etc.
        print(f"Job {job_id} completed successfully")
    elif status == "FAILED":
        # Alert about failure
        print(f"Job {job_id} failed")
    
    return {"success": True}
```

---

## Environment Setup

Quick development environment setup:

```bash
# Clone the repository
git clone https://github.com/your-org/nextflow-pipeline-platform.git
cd nextflow-pipeline-platform

# Run the setup script
./scripts/setup_dev.sh

# Start the backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload

# In a separate terminal, start the frontend
cd frontend
npm start
```
