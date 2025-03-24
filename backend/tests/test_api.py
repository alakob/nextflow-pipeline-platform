import json
import pytest
import os
import sys
from unittest.mock import patch, MagicMock

# Ensure imports work correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestAuthEndpoints:
    """Tests for authentication endpoints."""
    
    async def test_register(self, client):
        """Test user registration."""
        response = client.post(
            "/register",
            json={
                "username": "newuser",
                "password": "newpassword123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["username"] == "newuser"
    
    async def test_register_duplicate_username(self, client, test_user):
        """Test registration with an existing username."""
        response = client.post(
            "/register",
            json={
                "username": "testuser",
                "password": "password123"
            }
        )
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()
    
    async def test_login_success(self, client, test_user):
        """Test successful login."""
        response = client.post(
            "/login",
            data={
                "username": "testuser",
                "password": "password123"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    async def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials."""
        response = client.post(
            "/login",
            data={
                "username": "testuser",
                "password": "wrongpassword"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()
    
    async def test_get_current_user(self, client, user_token):
        """Test getting current user information."""
        response = client.get(
            "/users/me",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert "id" in data


class TestPipelineEndpoints:
    """Tests for pipeline endpoints."""
    
    async def test_list_pipelines(self, client, user_token, test_pipeline):
        """Test listing all pipelines."""
        response = client.get(
            "/pipelines",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any(p["name"] == "Test Pipeline" for p in data)
    
    async def test_get_pipeline(self, client, user_token, test_pipeline):
        """Test getting a specific pipeline."""
        response = client.get(
            f"/pipelines/{test_pipeline.id}",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Pipeline"
        assert data["description"] == "A pipeline for testing"
    
    async def test_get_nonexistent_pipeline(self, client, user_token):
        """Test getting a pipeline that doesn't exist."""
        response = client.get(
            "/pipelines/999",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 404


class TestJobEndpoints:
    """Tests for job endpoints."""
    
    @patch("app.routers.pipeline_router.pipeline_service.run_nextflow")
    async def test_submit_job(self, mock_run_nextflow, client, user_token, test_pipeline):
        """Test submitting a new job."""
        # Mock the pipeline execution function
        mock_run_nextflow.return_value = "12345"
        
        response = client.post(
            "/pipelines/jobs",
            json={
                "pipeline_id": test_pipeline.id,
                "params": {"sample": "test_sample"},
                "description": "API test job"
            },
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "queued"
        assert data["description"] == "API test job"
        
        # Verify the service was called
        mock_run_nextflow.assert_called_once()
    
    async def test_get_job(self, client, user_token, test_job):
        """Test getting a specific job."""
        response = client.get(
            f"/pipelines/jobs/{test_job.id}",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_job.id
        assert data["status"] == "queued"
    
    async def test_get_unauthorized_job(self, client, admin_token, test_job):
        """Test getting a job as another user (should fail unless admin)."""
        # Create a job for test_user but try to access it with a different user token
        # Admin can access any job
        response = client.get(
            f"/pipelines/jobs/{test_job.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
    
    async def test_list_jobs(self, client, user_token, test_job):
        """Test listing all jobs for the current user."""
        response = client.get(
            "/pipelines/jobs",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any(j["id"] == test_job.id for j in data)
    
    @patch("app.routers.pipeline_router.pipeline_service.cancel_nextflow")
    async def test_cancel_job(self, mock_cancel_nextflow, client, user_token, test_job, db_session):
        """Test canceling a job."""
        # Update the job to be in a running state for the test
        test_job.status = "running"
        test_job.process_id = "12345"
        await db_session.commit()
        
        # Mock the cancel function
        mock_cancel_nextflow.return_value = True
        
        response = client.delete(
            f"/pipelines/jobs/{test_job.id}",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "canceled"
        
        # Verify the service was called
        mock_cancel_nextflow.assert_called_once_with(test_job.process_id)


class TestPipelineIntegration:
    """Integration tests for pipeline execution."""
    
    @pytest.mark.integration
    @patch("app.services.pipeline_service.subprocess.Popen")
    async def test_pipeline_execution(self, mock_popen, client, user_token, test_pipeline):
        """Test the end-to-end pipeline execution flow."""
        # Mock the subprocess.Popen
        mock_process = MagicMock()
        mock_process.pid = 12345
        mock_process.stdout = MagicMock()
        mock_process.stderr = MagicMock()
        mock_popen.return_value = mock_process
        
        # Submit a job
        response = client.post(
            "/pipelines/jobs",
            json={
                "pipeline_id": test_pipeline.id,
                "params": {"outdir": "s3://nextflow-pipeline-data/test-output"},
                "description": "Integration test job"
            },
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 201
        job_data = response.json()
        job_id = job_data["id"]
        
        # Check the job status
        response = client.get(
            f"/pipelines/jobs/{job_id}",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 200
        status_data = response.json()
        assert status_data["status"] in ["queued", "running"]
        
        # Verify the subprocess.Popen was called with the correct arguments
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        command = args[0]
        assert "nextflow run" in command
        assert "s3://nextflow-pipeline-data" in command
