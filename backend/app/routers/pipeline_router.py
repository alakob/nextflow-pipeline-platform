from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from uuid import UUID
import json
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, validator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.database import get_db
from db.models import Job, Pipeline, User
from app.services import pipeline_service
from app.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/pipelines", tags=["pipelines"])


class PipelineParams(BaseModel):
    """Parameters for pipeline execution."""
    reads: Optional[str] = Field(None, description="Path to input reads")
    genome: Optional[str] = Field(None, description="Reference genome")
    max_memory: Optional[str] = Field("16.GB", description="Maximum memory to use")
    max_cpus: Optional[int] = Field(4, description="Maximum CPUs to use")
    custom_params: Optional[Dict[str, Any]] = Field(None, description="Additional pipeline parameters")


class PipelineBase(BaseModel):
    """Base pipeline model."""
    id: UUID
    name: str
    description: str


class PipelineResponse(PipelineBase):
    """Detailed pipeline response model."""
    nextflow_config: Optional[str] = None


class PipelineList(BaseModel):
    """Response model for a list of pipelines."""
    pipelines: List[PipelineBase]


@router.get("", response_model=PipelineList)
async def list_pipelines(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all available pipelines.
    """
    try:
        # Query for all pipelines
        result = await db.execute(select(Pipeline))
        pipelines = result.scalars().all()
        
        # Convert to response format
        pipeline_list = [
            {
                "id": pipeline.id,
                "name": pipeline.name,
                "description": pipeline.description,
            }
            for pipeline in pipelines
        ]
        
        return {"pipelines": pipeline_list}
    except Exception as e:
        # Log the error
        print(f"Error listing pipelines: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve pipelines: {str(e)}"
        )


class PipelineSubmission(BaseModel):
    """Pipeline job submission request."""
    pipeline_id: UUID
    params: Union[Dict[str, Any], str] = Field(default_factory=dict)
    description: Optional[str] = None

    @validator('params', pre=True)
    def validate_params(cls, v):
        """Validate and process the params field."""
        if v is None:
            return {}
            
        if isinstance(v, str):
            try:
                # Try to parse JSON string
                if v.strip():
                    return json.loads(v)
                else:
                    return {}
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON in params: {str(e)}")
                # Instead of raising an error, return empty dict
                return {}
        
        # If it's already a dict, return it
        if isinstance(v, dict):
            return v
            
        # For any other type, convert to empty dict
        logger.warning(f"Unexpected params type: {type(v)}, using empty dict")
        return {}


class JobResponse(BaseModel):
    """Job response model."""
    id: str
    job_id: str
    user_id: UUID
    pipeline_id: UUID
    pipeline_name: str
    status: str
    message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    external_id: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    work_dir: Optional[str] = None
    output_dir: Optional[str] = None
    params: Dict[str, Any] = Field(default_factory=dict)
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
    
    try:
        # Execute the pipeline with simulation mode
        job_meta = await pipeline_service.run_pipeline(
            pipeline_id=pipeline.id,
            user_id=current_user.id,
            params=submission.params,
            db=db,
            simulation_mode=True,
            description=submission.description
        )
        
        # Since we're now creating the job in the pipeline service,
        # we just need to fetch it from the database
        job_stmt = select(Job).where(Job.id == job_meta["job_id"])
        job_result = await db.execute(job_stmt)
        job = job_result.scalars().first()
        
        if not job:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Job was created but could not be retrieved"
            )
        
        # Return the response with a consistent format
        return {
            "id": job.id,
            "job_id": job.id,
            "user_id": job.user_id,
            "pipeline_id": job.pipeline_id,
            "pipeline_name": pipeline.name,
            "status": job.status,
            "message": job_meta.get("message"),
            "created_at": job.created_at,
            "updated_at": job.updated_at,
            "external_id": job.external_id,
            "started_at": job.started_at,
            "completed_at": job.completed_at,
            "work_dir": job.work_dir,
            "output_dir": job.output_dir,
            "params": job.params if isinstance(job.params, dict) else 
                     (json.loads(job.params) if isinstance(job.params, str) and job.params else {}),
            "description": job.description
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit pipeline job: {str(e)}"
        )


@router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_pipeline_job(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get pipeline job status and details."""
    # Query for the specific job
    stmt = select(Job).where(Job.id == job_id)
    result = await db.execute(stmt)
    job = result.scalars().first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with ID {job_id} not found"
        )
    
    # Check if user has access to this job
    if job.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this job"
        )
    
    # Get pipeline details
    pipeline_stmt = select(Pipeline).where(Pipeline.id == job.pipeline_id)
    pipeline_result = await db.execute(pipeline_stmt)
    pipeline = pipeline_result.scalars().first()
    
    if not pipeline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pipeline with ID {job.pipeline_id} not found"
        )
    
    # Return the job details with pipeline status
    # Make params handling more robust - handle both string and dict
    params_data = {}
    if job.params:
        if isinstance(job.params, dict):
            params_data = job.params
        elif isinstance(job.params, str):
            try:
                params_data = json.loads(job.params)
            except json.JSONDecodeError:
                logger.error(f"Failed to parse job params: {job.params}")
                params_data = {}
        else:
            logger.warning(f"Unexpected params type: {type(job.params)}")
    
    response_job = JobResponse(
        id=job.id,
        job_id=job.id,
        user_id=job.user_id,
        pipeline_id=job.pipeline_id,
        pipeline_name=pipeline.name,
        status=job.status,
        message=job.message,
        created_at=job.created_at,
        updated_at=job.updated_at,
        external_id=job.external_id,
        started_at=job.started_at,
        completed_at=job.completed_at,
        work_dir=job.work_dir,
        output_dir=job.output_dir,
        params=params_data,
        description=job.description
    )
    
    return response_job


@router.delete("/jobs/{job_id}", response_model=Dict[str, str])
async def cancel_pipeline_job(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Cancel a running pipeline job."""
    # Query for the specific job
    stmt = select(Job).where(Job.id == job_id)
    result = await db.execute(stmt)
    job = result.scalars().first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with ID {job_id} not found"
        )
    
    # Check if user has access to this job
    if job.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to cancel this job"
        )
    
    # Check if job is already in a terminal state
    if job.status in ["COMPLETED", "FAILED", "CANCELLED"]:
        return {
            "status": job.status,
            "message": f"Job is already in terminal state: {job.status}"
        }
    
    # Cancel the job
    cancel_result = await pipeline_service.cancel_pipeline(job_id, db)
    
    # Return the status
    return cancel_result


@router.get("/jobs", response_model=List[JobResponse])
async def list_pipeline_jobs(
    offset: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List pipeline jobs for the current user."""
    # Query for jobs depending on user role
    if current_user.role == "admin":
        # Admin sees all jobs
        stmt = select(Job).offset(offset).limit(limit)
    else:
        # Regular users only see their own jobs
        stmt = select(Job).where(Job.user_id == current_user.id).offset(offset).limit(limit)
    
    result = await db.execute(stmt)
    jobs = result.scalars().all()
    
    # Format the response
    response_jobs = []
    
    # Get all related pipelines to avoid N+1 queries
    pipeline_ids = {job.pipeline_id for job in jobs}
    pipelines_stmt = select(Pipeline).where(Pipeline.id.in_(pipeline_ids))
    pipelines_result = await db.execute(pipelines_stmt)
    pipelines = {p.id: p for p in pipelines_result.scalars().all()}
    
    for job in jobs:
        pipeline = pipelines.get(job.pipeline_id)
        pipeline_name = pipeline.name if pipeline else "Unknown Pipeline"
        
        # Make params handling more robust - handle both string and dict
        params_data = {}
        if job.params:
            if isinstance(job.params, dict):
                params_data = job.params
            elif isinstance(job.params, str):
                try:
                    params_data = json.loads(job.params)
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse job params: {job.params}")
                    params_data = {}
            else:
                logger.warning(f"Unexpected params type: {type(job.params)}")
                
        response_job = JobResponse(
            id=job.id,
            job_id=job.id,
            user_id=job.user_id,
            pipeline_id=job.pipeline_id,
            pipeline_name=pipeline_name,
            status=job.status,
            message=job.message,
            created_at=job.created_at,
            updated_at=job.updated_at,
            external_id=job.external_id,
            started_at=job.started_at,
            completed_at=job.completed_at,
            work_dir=job.work_dir,
            output_dir=job.output_dir,
            params=params_data,
            description=job.description
        )
        response_jobs.append(response_job)
    
    return response_jobs


@router.get("/jobs/{job_id}/download", response_model=Dict[str, str])
async def get_job_download_link(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate a download link for job results."""
    # Query for the specific job
    stmt = select(Job).where(Job.id == job_id)
    result = await db.execute(stmt)
    job = result.scalars().first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with ID {job_id} not found"
        )
    
    # Check if user has access to this job
    if job.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this job"
        )
    
    # Check if job is completed
    if job.status.lower() != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job is not completed. Download is only available for completed jobs."
        )
    
    # Check if output directory exists
    if not job.output_dir:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No output directory found for this job"
        )
    
    # Generate download link (in a real scenario, this would create a pre-signed URL or similar)
    # Here we'll just return the output directory path which frontend can use
    download_url = job.output_dir.replace("s3://", "https://download.example.com/")
    
    # In a production environment, you would create a time-limited signed URL
    # using the appropriate cloud provider's SDK (AWS, GCP, Azure, etc.)
    return {
        "download_url": download_url,
        "expires_in": "3600"  # URL valid for 1 hour (in seconds)
    }
