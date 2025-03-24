"""
Tests for API routes
"""
import os
import sys
import pytest
from uuid import UUID, uuid4
import json
from unittest.mock import patch, AsyncMock
from fastapi import status

# Import app routes for mocking
from app.routers import pipeline_router
from app.auth import create_access_token, verify_password, get_current_user
from app.services import pipeline_service

# Test the health check endpoint
def test_health_check(client):
    """Test the health check endpoint to verify the API is running."""
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "ok"}

# Test pipeline operations
def test_list_pipelines(client, test_pipeline):
    """Test listing available pipelines."""
    with patch("app.routers.pipeline_router.get_pipelines") as mock_get_pipelines:
        # Mock the pipeline listing
        mock_get_pipelines.return_value = AsyncMock(return_value=[
            {
                "id": str(test_pipeline.id),
                "name": test_pipeline.name,
                "description": test_pipeline.description,
                "created_at": test_pipeline.created_at.isoformat()
            }
        ])
        
        # Make the request
        response = client.get("/pipelines")
        
        # Check response
        assert response.status_code == status.HTTP_200_OK
        pipelines = response.json()
        assert isinstance(pipelines, list)
        assert len(pipelines) == 1
        assert pipelines[0]["id"] == str(test_pipeline.id)
        assert pipelines[0]["name"] == test_pipeline.name

def test_get_pipeline(client, test_pipeline):
    """Test retrieving a specific pipeline."""
    with patch("app.routers.pipeline_router.get_pipeline") as mock_get_pipeline:
        # Mock the pipeline retrieval
        mock_get_pipeline.return_value = AsyncMock(return_value={
            "id": str(test_pipeline.id),
            "name": test_pipeline.name,
            "description": test_pipeline.description,
            "nextflow_config": test_pipeline.nextflow_config,
            "created_at": test_pipeline.created_at.isoformat()
        })
        
        # Make the request
        response = client.get(f"/pipelines/{test_pipeline.id}")
        
        # Check response
        assert response.status_code == status.HTTP_200_OK
        pipeline = response.json()
        assert pipeline["id"] == str(test_pipeline.id)
        assert pipeline["name"] == test_pipeline.name

# Test job operations
def test_create_job(client, test_pipeline):
    """Test creating a new pipeline job."""
    # Mock get_pipeline
    with patch("app.routers.pipeline_router.get_pipeline") as mock_get_pipeline:
        mock_get_pipeline.return_value = AsyncMock(return_value={
            "id": str(test_pipeline.id),
            "name": test_pipeline.name,
            "description": test_pipeline.description,
            "nextflow_config": test_pipeline.nextflow_config
        })
        
        # Mock run_pipeline
        with patch("app.services.pipeline_service.run_pipeline", new_callable=AsyncMock) as mock_run:
            # Test data
            job_data = {
                "pipeline_id": str(test_pipeline.id),
                "parameters": {
                    "input": "s3://test-bucket/sample.fastq",
                    "output_dir": "s3://test-bucket/results/"
                }
            }
            
            # Make the request
            response = client.post(
                "/pipelines/jobs",
                json=job_data
            )
            
            # Check response
            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            assert "id" in data
            assert data["status"] in ["SUBMITTED", "QUEUED"]
            
            # Verify run_pipeline was called
            mock_run.assert_called_once()

def test_get_job(client, test_job):
    """Test retrieving a job by ID."""
    with patch("app.routers.pipeline_router.get_job") as mock_get_job:
        # Mock the job lookup
        mock_get_job.return_value = AsyncMock(return_value={
            "id": str(test_job.id),
            "user_id": str(test_job.user_id),
            "pipeline_id": str(test_job.pipeline_id),
            "status": test_job.status,
            "parameters": json.loads(test_job.parameters),
            "external_id": test_job.external_id,
            "work_dir": test_job.work_dir,
            "output_dir": test_job.output_dir,
            "created_at": test_job.created_at.isoformat()
        })
        
        # Make the request
        response = client.get(f"/pipelines/jobs/{test_job.id}")
        
        # Check response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == str(test_job.id)
        assert data["status"] == test_job.status

def test_list_jobs(client, test_job):
    """Test listing all jobs for a user."""
    with patch("app.routers.pipeline_router.get_user_jobs") as mock_get_user_jobs:
        # Mock the job listing
        mock_get_user_jobs.return_value = AsyncMock(return_value=[
            {
                "id": str(test_job.id),
                "pipeline_id": str(test_job.pipeline_id),
                "status": test_job.status,
                "created_at": test_job.created_at.isoformat()
            }
        ])
        
        # Make the request
        response = client.get("/pipelines/jobs")
        
        # Check response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["id"] == str(test_job.id)
        assert data[0]["status"] == test_job.status

def test_cancel_job(client, test_job):
    """Test canceling a job."""
    with patch("app.routers.pipeline_router.get_job") as mock_get_job:
        # Mock the job lookup
        mock_get_job.return_value = AsyncMock(return_value={
            "id": str(test_job.id),
            "user_id": str(test_job.user_id),
            "pipeline_id": str(test_job.pipeline_id),
            "status": "RUNNING",
            "external_id": "batch-job-123"
        })
        
        # Mock the cancel_pipeline function
        with patch("app.services.pipeline_service.cancel_pipeline", new_callable=AsyncMock) as mock_cancel:
            mock_cancel.return_value = {"status": "cancelled"}
            
            # Make the request
            response = client.delete(f"/pipelines/jobs/{test_job.id}")
            
            # Check response
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["status"] == "cancelled"
            
            # Verify cancel_pipeline was called
            mock_cancel.assert_called_once()

# Test authentication
def test_login(client, test_user):
    """Test the login endpoint."""
    # Test password verification
    with patch("app.auth.verify_password") as mock_verify:
        mock_verify.return_value = True  # Simulate successful password verification
        
        # Mock the token creation
        with patch("app.auth.create_access_token") as mock_token:
            mock_token.return_value = "test_token"
            
            # Make the login request
            response = client.post(
                "/auth/token",
                data={"username": test_user.username, "password": "password123"}
            )
            
            # Check response
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "access_token" in data
            assert data["token_type"] == "bearer"
