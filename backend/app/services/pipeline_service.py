import asyncio
import logging
import os
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Job, Pipeline, User

logger = logging.getLogger(__name__)

# Pipeline execution configurations
PIPELINE_DIR = str(Path(__file__).parents[3] / "pipeline")
AWS_REGION = "eu-north-1"
S3_BUCKET = "nextflow-pipeline-data-nto15x4w"  # This should be retrieved from environment or configuration

# Ensure the directory exists
os.makedirs(PIPELINE_DIR, exist_ok=True)


async def run_pipeline(
    pipeline_id: UUID,
    user_id: UUID,
    params: Dict[str, Any],
    db: AsyncSession,
    simulation_mode: bool = True,
    description: str = None
) -> Dict[str, Any]:
    """
    Run a Nextflow pipeline asynchronously.
    
    Args:
        pipeline_id: UUID of the pipeline to run
        user_id: UUID of the user who initiated the pipeline
        params: Dictionary of parameters to pass to the pipeline
        db: Database session
        simulation_mode: If True, simulate pipeline execution instead of running actual commands
        description: Optional description of the job
        
    Returns:
        Dictionary containing job metadata
    """
    # Generate a unique job ID
    job_id = f"job-{datetime.now().strftime('%Y%m%d%H%M%S')}-{user_id.hex[:6]}"
    work_dir = f"s3://{S3_BUCKET}/work/{job_id}"
    output_dir = f"s3://{S3_BUCKET}/results/{job_id}"
    
    # Get pipeline details from database
    pipeline_result = await db.execute(select(Pipeline).where(Pipeline.id == pipeline_id))
    pipeline = pipeline_result.scalars().first()
    
    if not pipeline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pipeline with ID {pipeline_id} not found"
        )
    
    try:
        # In simulation mode, we don't actually run Nextflow commands
        if simulation_mode:
            logger.info(f"SIMULATION: Starting pipeline {pipeline.name} (ID: {pipeline_id}) with parameters: {json.dumps(params)}")
            
            # Create a job entry in the database
            new_job = Job(
                id=job_id,
                pipeline_id=pipeline_id,
                user_id=user_id,
                status="SUBMITTED",
                params=params,  # Store as direct dict since we're using JSON column type
                work_dir=work_dir,
                output_dir=output_dir,
                description=description
            )
            
            db.add(new_job)
            await db.commit()
            await db.refresh(new_job)
            
            # Simulate async pipeline execution by not waiting
            # In a real implementation, this would spawn a background task
            
            return {
                "job_id": job_id,
                "pipeline_id": pipeline_id,
                "pipeline_name": pipeline.name,
                "user_id": user_id,
                "status": "SUBMITTED",
                "work_dir": work_dir,
                "output_dir": output_dir,
                "started_at": datetime.now().isoformat(),
                "params": params,
                "description": description,
                "message": f"Job submitted successfully and is queued for processing"
            }
        else:
            # This is the real implementation that would use Nextflow
            # Currently not implemented for development
            raise NotImplementedError("Real pipeline execution is not implemented in development mode")
            
    except Exception as e:
        logger.error(f"Failed to start pipeline {pipeline_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start pipeline: {str(e)}"
        )


async def get_pipeline_status(job_id: str, db: AsyncSession) -> Dict[str, Any]:
    """
    Get the status of a running pipeline.
    
    Args:
        job_id: ID of the job to check
        db: Database session
        
    Returns:
        Dictionary containing job status information
    """
    # Look up job in the database
    job_result = await db.execute(select(Job).where(Job.id == job_id))
    job = job_result.scalars().first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with ID {job_id} not found"
        )
    
    # Get pipeline details
    pipeline_result = await db.execute(select(Pipeline).where(Pipeline.id == job.pipeline_id))
    pipeline = pipeline_result.scalars().first()
    
    if not pipeline:
        logger.error(f"Pipeline not found for job {job_id}")
        return {
            "status": "ERROR",
            "error": "Associated pipeline not found"
        }
    
    # In a real implementation, this would check the actual status
    # For simulation, we just return the stored status
    return {
        "job_id": job.id,
        "pipeline_id": str(job.pipeline_id),
        "pipeline_name": pipeline.name,
        "user_id": str(job.user_id),
        "status": job.status,
        "started_at": job.created_at.isoformat() if job.created_at else None,
        "completed_at": job.updated_at.isoformat() if job.updated_at and job.status in ["COMPLETED", "FAILED", "CANCELLED"] else None,
        "params": job.params,
        "work_dir": job.work_dir,
        "output_dir": job.output_dir
    }


async def cancel_pipeline(job_id: str, db: AsyncSession) -> Dict[str, Any]:
    """
    Cancel a running pipeline.
    
    Args:
        job_id: ID of the job to cancel
        db: Database session
        
    Returns:
        Dictionary containing job status information
    """
    # Look up job in the database
    job_result = await db.execute(select(Job).where(Job.id == job_id))
    job = job_result.scalars().first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with ID {job_id} not found"
        )
    
    if job.status in ["COMPLETED", "FAILED", "CANCELLED"]:
        return {
            "status": job.status,
            "message": f"Job already in terminal state: {job.status}"
        }
    
    # Update job status
    job.status = "CANCELLED"
    await db.commit()
    
    logger.info(f"SIMULATION: Cancelled job {job_id}")
    
    return {
        "status": "CANCELLED",
        "message": "Job cancelled successfully"
    }
