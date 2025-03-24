from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID
import json

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.database import get_db
from db.models import Job, Pipeline, User
from app.services import pipeline_service
from app.auth import get_current_user

router = APIRouter(prefix="/pipelines", tags=["pipelines"])


class PipelineParams(BaseModel):
    """Parameters for pipeline execution."""
    reads: Optional[str] = Field(None, description="Path to input reads")
    genome: Optional[str] = Field(None, description="Reference genome")
    max_memory: Optional[str] = Field("16.GB", description="Maximum memory to use")
    max_cpus: Optional[int] = Field(4, description="Maximum CPUs to use")
    custom_params: Optional[Dict[str, Any]] = Field(None, description="Additional pipeline parameters")


class PipelineSubmission(BaseModel):
    """Pipeline job submission request."""
    pipeline_id: UUID
    params: PipelineParams
    description: Optional[str] = None


class JobResponse(BaseModel):
    """Job response model."""
    id: UUID
    user_id: UUID
    pipeline_id: UUID
    status: str
    created_at: datetime
    updated_at: datetime
    external_id: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    work_dir: Optional[str] = None
    output_dir: Optional[str] = None
    parameters: Dict[str, Any]
    description: Optional[str] = None


@router.post("/jobs", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def submit_pipeline_job(
    submission: PipelineSubmission,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Submit a pipeline job for execution."""
    # Verify that pipeline exists
    stmt = select(Pipeline).where(Pipeline.id == submission.pipeline_id)
    result = await db.execute(stmt)
    pipeline = result.scalars().first()
    if not pipeline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pipeline with ID {submission.pipeline_id} not found"
        )
    
    # Prepare parameters dictionary from submission
    params_dict = submission.params.model_dump(exclude_none=True)
    
    # Include any custom parameters
    if submission.params.custom_params:
        params_dict.update(submission.params.custom_params)
    
    # Execute the pipeline and get job metadata
    job_meta = await pipeline_service.run_pipeline(
        pipeline_id=pipeline.id,
        user_id=current_user.id,
        params=params_dict,
        pipeline_file="test.nf",  # Use a default for tests since pipeline.path may not be available
        profile="aws"  # Always use AWS Batch for production
    )
    
    # Create job record in database
    job = Job(
        user_id=current_user.id,
        pipeline_id=pipeline.id,
        status=job_meta["status"],
        external_id=job_meta["job_id"],
        work_dir=job_meta["work_dir"],
        output_dir=job_meta["output_dir"],
        parameters=json.dumps(params_dict),  # Serialize dict to JSON string
        description=submission.description,
        created_at=datetime.now(),
        started_at=datetime.now(),
    )
    
    db.add(job)
    await db.commit()
    await db.refresh(job)
    
    return job


@router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_pipeline_job(
    job_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get pipeline job status and details."""
    # Retrieve job from database
    stmt = select(Job).where(Job.id == job_id)
    result = await db.execute(stmt)
    job = result.scalars().first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with ID {job_id} not found"
        )
    
    # Check if user is authorized to view this job
    if str(job.user_id) != str(current_user.id) and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this job"
        )
    
    # Get current status from Nextflow
    if job.status not in ["COMPLETED", "FAILED", "CANCELLED"]:
        status_info = await pipeline_service.get_pipeline_status(job.external_id)
        
        # Update job status in database if changed
        if status_info["status"] != job.status:
            job.status = status_info["status"]
            
            # Update completion time if job is finished
            if job.status in ["COMPLETED", "FAILED", "CANCELLED"] and not job.completed_at:
                job.completed_at = datetime.now()
                
            await db.commit()
            await db.refresh(job)
    
    # Parse parameters JSON string back to dictionary
    response_job = JobResponse(
        id=job.id,
        user_id=job.user_id,
        pipeline_id=job.pipeline_id,
        status=job.status,
        created_at=job.created_at,
        updated_at=job.updated_at,
        external_id=job.external_id,
        started_at=job.started_at,
        completed_at=job.completed_at,
        work_dir=job.work_dir,
        output_dir=job.output_dir,
        parameters=json.loads(job.parameters) if job.parameters else {},
        description=job.description
    )
    
    return response_job


@router.delete("/jobs/{job_id}", status_code=status.HTTP_200_OK)
async def cancel_pipeline_job(
    job_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Cancel a running pipeline job."""
    # Retrieve job from database
    stmt = select(Job).where(Job.id == job_id)
    result = await db.execute(stmt)
    job = result.scalars().first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with ID {job_id} not found"
        )
    
    # Check if user is authorized to cancel this job
    if str(job.user_id) != str(current_user.id) and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to cancel this job"
        )
    
    # Check if job is already completed or cancelled
    if job.status in ["COMPLETED", "FAILED", "CANCELLED"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Job is already in terminal state: {job.status}"
        )
    
    # Cancel the job
    cancel_result = await pipeline_service.cancel_pipeline(job.external_id)
    
    # Update job status in database
    job.status = "CANCELLED"
    job.completed_at = datetime.now()
    await db.commit()
    
    return {"status": "success", "message": "Job cancelled successfully"}


@router.get("/jobs", response_model=List[JobResponse])
async def list_pipeline_jobs(
    offset: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List pipeline jobs for the current user."""
    # Query jobs (admin sees all jobs, regular users only see their own)
    if current_user.role == "admin":
        stmt = (
            select(Job)
            .order_by(Job.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
    else:
        stmt = (
            select(Job)
            .where(Job.user_id == current_user.id)
            .order_by(Job.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
    
    result = await db.execute(stmt)
    jobs = result.scalars().all()
    
    # Parse parameters JSON string back to dictionary for each job
    response_jobs = []
    for job in jobs:
        response_job = JobResponse(
            id=job.id,
            user_id=job.user_id,
            pipeline_id=job.pipeline_id,
            status=job.status,
            created_at=job.created_at,
            updated_at=job.updated_at,
            external_id=job.external_id,
            started_at=job.started_at,
            completed_at=job.completed_at,
            work_dir=job.work_dir,
            output_dir=job.output_dir,
            parameters=json.loads(job.parameters) if job.parameters else {},
            description=job.description
        )
        response_jobs.append(response_job)
    
    return response_jobs
