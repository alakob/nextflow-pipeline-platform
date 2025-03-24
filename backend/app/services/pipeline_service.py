import asyncio
import logging
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from fastapi import HTTPException, status

logger = logging.getLogger(__name__)

# Pipeline execution configurations
NEXTFLOW_BIN = str(Path(__file__).parents[3] / "pipeline" / "nextflow")
PIPELINE_DIR = str(Path(__file__).parents[3] / "pipeline")
AWS_REGION = "eu-north-1"
S3_BUCKET = "nextflow-pipeline-data-nto15x4w"  # This should be retrieved from environment or configuration

# Ensure the JAVA_HOME environment variable is set when running Nextflow
os.environ["PATH"] = "/opt/homebrew/opt/openjdk@17/bin:" + os.environ.get("PATH", "")


async def run_pipeline(
    pipeline_id: UUID,
    user_id: UUID,
    params: Dict[str, Any],
    pipeline_file: str = "test.nf",
    profile: str = "aws",
) -> Dict[str, Any]:
    """
    Run a Nextflow pipeline asynchronously.
    
    Args:
        pipeline_id: UUID of the pipeline to run
        user_id: UUID of the user who initiated the pipeline
        params: Dictionary of parameters to pass to the pipeline
        pipeline_file: Path to the Nextflow pipeline file to run
        profile: Nextflow profile to use (local, docker, aws)
        
    Returns:
        Dictionary containing job metadata
    """
    job_id = f"job-{datetime.now().strftime('%Y%m%d%H%M%S')}-{user_id.hex[:6]}"
    work_dir = f"s3://{S3_BUCKET}/work/{job_id}"
    output_dir = f"s3://{S3_BUCKET}/results/{job_id}"
    
    # Build the Nextflow command
    cmd = [
        NEXTFLOW_BIN,
        "run",
        pipeline_file,
        "-profile", profile,
        "--outdir", output_dir,
        "-w", work_dir,
        "-name", job_id,
    ]
    
    # Add any additional parameters
    for key, value in params.items():
        if value is not None:
            cmd.extend([f"--{key}", str(value)])
    
    logger.info(f"Starting pipeline {pipeline_id} with command: {' '.join(cmd)}")
    
    try:
        # Run the Nextflow command asynchronously
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=PIPELINE_DIR
        )
        
        # Return job metadata immediately without waiting for completion
        return {
            "job_id": job_id,
            "pipeline_id": pipeline_id,
            "user_id": user_id,
            "status": "SUBMITTED",
            "work_dir": work_dir,
            "output_dir": output_dir,
            "started_at": datetime.now().isoformat(),
            "params": params,
        }
    except Exception as e:
        logger.error(f"Failed to start pipeline {pipeline_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start pipeline: {str(e)}"
        )


async def get_pipeline_status(job_id: str) -> Dict[str, Any]:
    """
    Get the status of a running pipeline.
    
    Args:
        job_id: ID of the job to check
        
    Returns:
        Dictionary containing job status information
    """
    cmd = [
        NEXTFLOW_BIN,
        "log",
        job_id,
        "-f", "status,duration,complete,error"
    ]
    
    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=PIPELINE_DIR
        )
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            logger.error(f"Failed to get status for job {job_id}: {stderr.decode()}")
            return {"status": "UNKNOWN", "error": stderr.decode()}
        
        # Parse the output
        output = stdout.decode().strip()
        if not output:
            return {"status": "RUNNING", "progress": "Initializing"}
        
        lines = output.split('\n')
        if len(lines) < 2:  # No data or header only
            return {"status": "RUNNING", "progress": "Initializing"}
        
        # Skip the header line
        status_line = lines[1].split(',')
        if len(status_line) >= 4:
            status, duration, complete, error = status_line
            return {
                "status": "COMPLETED" if complete.lower() == "true" else "RUNNING" if error.lower() == "false" else "FAILED",
                "duration": duration,
                "error": error if error.lower() != "false" else None
            }
        
        return {"status": "RUNNING", "progress": "In progress"}
    except Exception as e:
        logger.error(f"Error getting pipeline status for {job_id}: {str(e)}")
        return {"status": "ERROR", "error": str(e)}


async def cancel_pipeline(job_id: str) -> Dict[str, Any]:
    """
    Cancel a running pipeline.
    
    Args:
        job_id: ID of the job to cancel
        
    Returns:
        Dictionary containing job status information
    """
    cmd = [
        NEXTFLOW_BIN,
        "cancel",
        job_id
    ]
    
    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=PIPELINE_DIR
        )
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            logger.error(f"Failed to cancel job {job_id}: {stderr.decode()}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to cancel job: {stderr.decode()}"
            )
        
        return {"status": "CANCELLED", "message": "Job cancelled successfully"}
    except Exception as e:
        logger.error(f"Error cancelling pipeline {job_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error cancelling pipeline: {str(e)}"
        )
