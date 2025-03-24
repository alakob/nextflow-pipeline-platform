# API Documentation

> ⏱️ **Time to read**: 15 minutes  
> 🗓️ **Last updated**: March 24, 2025

## Table of Contents

- [Introduction](#introduction)
- [Authentication](#authentication)
- [API Endpoints](#api-endpoints)
  - [Health Check](#health-check)
  - [User Management](#user-management)
  - [Pipeline Management](#pipeline-management)
  - [Job Management](#job-management)
- [Error Responses](#error-responses)
- [Pagination](#pagination)
- [Rate Limiting](#rate-limiting)
- [API Versioning](#api-versioning)
- [Webhooks](#webhooks)
- [Example Use Cases](#example-use-cases)

## Introduction

This document provides a comprehensive reference for the Nextflow Pipeline Platform API endpoints. The API follows RESTful principles and uses JSON for request and response bodies.

**Base URL**:
- Development: `http://localhost:8000`
- Production: `https://api.your-domain.com`

## Authentication

The API uses JSON Web Tokens (JWT) for authentication with a 30-minute default expiration time.

### Obtaining a Token

```http
POST /auth/token
```

**Request Body:**
```json
{
  "username": "your_username",
  "password": "your_password"
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Using Authentication

Include the token in the `Authorization` header:

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Token Lifetime:** Tokens expire after 30 minutes by default. You'll need to request a new token after expiration.

## API Endpoints

### Health Check

> 🟢 **No Authentication Required**

```http
GET /
```

**cURL Example:**
```bash
curl -X GET http://localhost:8000/
```

**Response:**
```json
{
  "status": "ok"
}
```

### User Management

#### Register User

> 🟢 **No Authentication Required**

```http
POST /register
```

**Request Body:**
```json
{
  "username": "new_user",
  "password": "secure_password"
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{"username": "new_user", "password": "secure_password"}'
```

**Response:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "username": "new_user"
}
```

#### Get Current User

> 🔒 **Authentication Required**

```http
GET /users/me
```

**cURL Example:**
```bash
curl -X GET http://localhost:8000/users/me \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "username": "your_username",
  "role": "user"
}
```

### Pipeline Management

#### List Pipelines

> 🔒 **Authentication Required**

```http
GET /pipelines
```

**Query Parameters:**
- `offset` (optional): Number of items to skip (default: 0)
- `limit` (optional): Maximum number of items to return (default: 100)

**cURL Example:**
```bash
curl -X GET "http://localhost:8000/pipelines?limit=10" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response:**
```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "name": "RNA-Seq Analysis",
    "description": "Standard RNA-Seq analysis pipeline",
    "created_at": "2025-01-15T12:00:00"
  },
  {
    "id": "223e4567-e89b-12d3-a456-426614174000",
    "name": "Variant Calling",
    "description": "Genomic variant calling pipeline",
    "created_at": "2025-01-20T09:30:00"
  }
]
```

#### Get Pipeline Details

> 🔒 **Authentication Required**

```http
GET /pipelines/{pipeline_id}
```

**Path Parameters:**
- `pipeline_id`: UUID of the pipeline

**cURL Example:**
```bash
curl -X GET http://localhost:8000/pipelines/123e4567-e89b-12d3-a456-426614174000 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "RNA-Seq Analysis",
  "description": "Standard RNA-Seq analysis pipeline",
  "nextflow_config": "process {\n  executor = 'awsbatch'\n  ...",
  "created_at": "2025-01-15T12:00:00"
}
```

### Job Management

#### Submit Pipeline Job

> 🔒 **Authentication Required**

```http
POST /pipelines/jobs
```

**Request Body:**
```json
{
  "pipeline_id": "123e4567-e89b-12d3-a456-426614174000",
  "params": {
    "reads": "s3://example-bucket/reads/*.fastq",
    "genome": "s3://example-bucket/reference/genome.fa",
    "max_memory": "16.GB",
    "max_cpus": 4
  },
  "description": "RNA-Seq analysis of sample XYZ"
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/pipelines/jobs \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -d '{
    "pipeline_id": "123e4567-e89b-12d3-a456-426614174000",
    "params": {
      "reads": "s3://example-bucket/reads/*.fastq",
      "genome": "s3://example-bucket/reference/genome.fa",
      "max_memory": "16.GB",
      "max_cpus": 4
    },
    "description": "RNA-Seq analysis of sample XYZ"
  }'
```

**Response:**
```json
{
  "id": "323e4567-e89b-12d3-a456-426614174000",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "pipeline_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "SUBMITTED",
  "created_at": "2025-03-01T14:30:00",
  "updated_at": "2025-03-01T14:30:00"
}
```

#### Get Job Status

> 🔒 **Authentication Required**

```http
GET /pipelines/jobs/{job_id}
```

**Path Parameters:**
- `job_id`: UUID of the job

**cURL Example:**
```bash
curl -X GET http://localhost:8000/pipelines/jobs/323e4567-e89b-12d3-a456-426614174000 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response:**
```json
{
  "id": "323e4567-e89b-12d3-a456-426614174000",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "pipeline_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "RUNNING",
  "parameters": {
    "reads": "s3://example-bucket/reads/*.fastq",
    "genome": "s3://example-bucket/reference/genome.fa",
    "max_memory": "16.GB",
    "max_cpus": 4
  },
  "external_id": "batch-job-123",
  "work_dir": "s3://nextflow-pipeline-data-nto15x4w/work/job-20250301143000-123abc",
  "output_dir": "s3://nextflow-pipeline-data-nto15x4w/results/job-20250301143000-123abc",
  "created_at": "2025-03-01T14:30:00",
  "updated_at": "2025-03-01T14:35:00",
  "started_at": "2025-03-01T14:32:00",
  "completed_at": null,
  "description": "RNA-Seq analysis of sample XYZ"
}
```

#### List Jobs

> 🔒 **Authentication Required**

```http
GET /pipelines/jobs
```

**Query Parameters:**
- `offset` (optional): Number of items to skip (default: 0)
- `limit` (optional): Maximum number of items to return (default: 100)
- `status` (optional): Filter by job status (e.g., SUBMITTED, RUNNING, COMPLETED, FAILED)

**cURL Example:**
```bash
curl -X GET "http://localhost:8000/pipelines/jobs?limit=10&status=RUNNING" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response:**
```json
[
  {
    "id": "323e4567-e89b-12d3-a456-426614174000",
    "pipeline_id": "123e4567-e89b-12d3-a456-426614174000",
    "status": "RUNNING",
    "created_at": "2025-03-01T14:30:00",
    "description": "RNA-Seq analysis of sample XYZ"
  },
  {
    "id": "423e4567-e89b-12d3-a456-426614174000",
    "pipeline_id": "223e4567-e89b-12d3-a456-426614174000",
    "status": "RUNNING",
    "created_at": "2025-02-28T09:15:00",
    "description": "Variant calling for sample ABC"
  }
]
```

#### Cancel Job

> 🔒 **Authentication Required**

```http
DELETE /pipelines/jobs/{job_id}
```

**Path Parameters:**
- `job_id`: UUID of the job

**cURL Example:**
```bash
curl -X DELETE http://localhost:8000/pipelines/jobs/323e4567-e89b-12d3-a456-426614174000 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response:**
```json
{
  "status": "cancelled"
}
```

## Error Responses

The API uses standard HTTP status codes and returns detailed error messages in JSON format.

### 400 Bad Request

```json
{
  "detail": "Invalid input: Pipeline ID is required"
}
```

### 401 Unauthorized

```json
{
  "detail": "Could not validate credentials",
  "headers": {
    "WWW-Authenticate": "Bearer"
  }
}
```

### 403 Forbidden

```json
{
  "detail": "Not authorized to access this resource"
}
```

### 404 Not Found

```json
{
  "detail": "Job with ID 123e4567-e89b-12d3-a456-426614174000 not found"
}
```

### 500 Internal Server Error

```json
{
  "detail": "An unexpected error occurred"
}
```

## Pagination

Endpoints that return lists support pagination through the `offset` and `limit` query parameters:

```http
GET /pipelines/jobs?offset=10&limit=20
```

**Response Headers:**
```
X-Total-Count: 45
X-Page-Size: 20
```

## Rate Limiting

API requests are rate-limited to protect the service. Limits are:
- 100 requests per minute for authenticated users
- 20 requests per minute for unauthenticated requests

When the rate limit is exceeded, the API returns a 429 Too Many Requests response with headers indicating the rate limit status:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1616985412
```

## API Versioning

The current API version is v1. All endpoints are prefixed with `/api/v1` in production to support future versioning:

```
https://api.your-domain.com/api/v1/pipelines
```

## Webhooks

The API supports webhooks for job status notifications:

### Register a Webhook

> 🔒 **Authentication Required**

```http
POST /webhooks
```
   
**Request Body:**
```json
{
  "url": "https://your-service.com/webhook",
  "events": ["job.completed", "job.failed"]
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/webhooks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -d '{
    "url": "https://your-service.com/webhook",
    "events": ["job.completed", "job.failed"]
  }'
```

**Response:**
```json
{
  "id": "523e4567-e89b-12d3-a456-426614174000",
  "url": "https://your-service.com/webhook",
  "events": ["job.completed", "job.failed"],
  "created_at": "2025-03-01T14:30:00"
}
```

### Webhook Payload Example

```json
{
  "event": "job.completed",
  "job_id": "323e4567-e89b-12d3-a456-426614174000",
  "status": "COMPLETED",
  "timestamp": "2025-03-01T16:45:00",
  "output_dir": "s3://nextflow-pipeline-data-nto15x4w/results/job-20250301143000-123abc"
}
```

## Example Use Cases

### Complete Workflow: Run a Pipeline Job and Monitor Status

1. **Authenticate**:
   ```bash
   curl -X POST http://localhost:8000/auth/token \
     -H "Content-Type: application/json" \
     -d '{"username": "your_username", "password": "your_password"}'
   ```

2. **List available pipelines**:
   ```bash
   curl -X GET http://localhost:8000/pipelines \
     -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
   ```

3. **Submit a job**:
   ```bash
   curl -X POST http://localhost:8000/pipelines/jobs \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
     -d '{
       "pipeline_id": "123e4567-e89b-12d3-a456-426614174000",
       "params": {
         "reads": "s3://example-bucket/reads/*.fastq",
         "genome": "s3://example-bucket/reference/genome.fa"
       }
     }'
   ```

4. **Check job status**:
   ```bash
   curl -X GET http://localhost:8000/pipelines/jobs/323e4567-e89b-12d3-a456-426614174000 \
     -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
   ```

---

**Next Steps**:
- [Backend Development Guide](./backend_development.md)
- [User Guide](./user_guide.md)
- [Pipeline Development Guide](./pipeline_development.md)
