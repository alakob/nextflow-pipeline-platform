import os
import sys
import pytest
import boto3
import time
from unittest.mock import patch
import json
from datetime import datetime, timedelta

# Ensure imports work correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.pipeline_service import run_nextflow, check_job_status, cancel_nextflow
from db.models import Job, Pipeline, User


class TestAWSBatchIntegration:
    """Integration tests specifically for AWS Batch execution."""
    
    @pytest.mark.aws
    @pytest.mark.integration
    async def test_aws_batch_job_submission(self, db_session, test_user, test_pipeline):
        """
        Test submitting a Nextflow job to AWS Batch.
        
        This test requires AWS credentials to be configured and will actually submit
        a small test job to AWS Batch, so it should be run selectively.
        """
        # Create a unique job ID for testing
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        test_job_desc = f"AWS Batch integration test {timestamp}"
        
        # Create job record in database
        job = Job(
            user_id=test_user.id,
            pipeline_id=test_pipeline.id,
            status="created",
            params={"outdir": f"s3://nextflow-pipeline-data/test-{timestamp}"},
            description=test_job_desc
        )
        db_session.add(job)
        await db_session.commit()
        await db_session.refresh(job)
        
        try:
            # Run the actual Nextflow pipeline submission
            process_id = await run_nextflow(
                job_id=job.id,
                pipeline_id=test_pipeline.id,
                parameters=json.dumps(job.params),
                user_id=test_user.id
            )
            
            # Update job with process ID
            job.process_id = process_id
            job.status = "running"
            await db_session.commit()
            
            # Check that process_id is not None
            assert process_id is not None
            
            # Wait and check job status (with timeout)
            start_time = time.time()
            max_wait_time = 300  # 5 minutes
            job_running = False
            
            while time.time() - start_time < max_wait_time:
                # Check job status
                status = await check_job_status(job.id)
                
                # If job is actively running in AWS Batch, mark test as passed
                if status in ["running", "completed"]:
                    job_running = True
                    break
                
                # If job failed, test has failed
                if status in ["failed", "canceled"]:
                    break
                
                # Wait before checking again
                time.sleep(15)
            
            # Verify the job was successfully submitted and started running
            assert job_running, f"Job did not reach running state within {max_wait_time} seconds"
            
        finally:
            # Cleanup: Cancel job if still running
            try:
                if job.status in ["queued", "running"]:
                    await cancel_nextflow(job.process_id)
                    job.status = "canceled"
                    await db_session.commit()
            except Exception as e:
                print(f"Error during cleanup: {e}")
    
    @pytest.mark.aws
    @pytest.mark.integration
    async def test_aws_batch_job_cancellation(self, db_session, test_user, test_pipeline):
        """
        Test canceling a running Nextflow job on AWS Batch.
        
        This test requires AWS credentials to be configured and will actually submit
        and then cancel a job on AWS Batch.
        """
        # Create a unique job ID for testing
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        test_job_desc = f"AWS Batch cancel test {timestamp}"
        
        # Create job record in database
        job = Job(
            user_id=test_user.id,
            pipeline_id=test_pipeline.id,
            status="created",
            params={"outdir": f"s3://nextflow-pipeline-data/cancel-test-{timestamp}"},
            description=test_job_desc
        )
        db_session.add(job)
        await db_session.commit()
        await db_session.refresh(job)
        
        try:
            # Run the actual Nextflow pipeline submission
            process_id = await run_nextflow(
                job_id=job.id,
                pipeline_id=test_pipeline.id,
                parameters=json.dumps(job.params),
                user_id=test_user.id
            )
            
            # Update job with process ID
            job.process_id = process_id
            job.status = "running"
            await db_session.commit()
            
            assert process_id is not None
            
            # Wait a bit to ensure the job is submitted
            time.sleep(10)
            
            # Cancel the job
            cancel_success = await cancel_nextflow(process_id)
            
            # Update job status
            if cancel_success:
                job.status = "canceled"
                await db_session.commit()
            
            # Verify cancellation was successful
            assert cancel_success, "Failed to cancel job"
            
            # Verify job status has been updated
            status = await check_job_status(job.id)
            assert status in ["canceled", "stopping"], f"Job status should be canceled, but is {status}"
            
        except Exception as e:
            # Ensure we attempt to cancel in case of test failure
            if job.process_id:
                try:
                    await cancel_nextflow(job.process_id)
                except:
                    pass
            raise e


# AWS Batch monitoring utility
class AWSBatchUtils:
    """Utility methods for interacting with AWS Batch."""
    
    @staticmethod
    def get_job_status(job_id):
        """Get the status of an AWS Batch job."""
        try:
            batch_client = boto3.client('batch', region_name='eu-north-1')
            response = batch_client.describe_jobs(jobs=[job_id])
            
            if response['jobs']:
                return response['jobs'][0]['status']
            return None
        except Exception as e:
            print(f"Error checking AWS Batch job status: {e}")
            return None
