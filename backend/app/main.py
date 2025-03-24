from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, Any, List, Optional
from uuid import UUID
from pydantic import BaseModel, Field

from db.database import get_db
from db.models import User, Job, Pipeline
from app.auth import get_password_hash, verify_password, create_access_token, get_current_user
from app.routers import pipeline_router
from app.services.pipeline_service import run_pipeline, get_pipeline_status, cancel_pipeline

# Define Pydantic models for request and response validation
class UserCreate(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: UUID
    username: str
    role: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class JobCreate(BaseModel):
    pipeline_id: UUID
    description: Optional[str] = None
    params: Dict[str, Any] = Field(default_factory=dict)

class JobResponse(BaseModel):
    job_id: str
    pipeline_id: UUID
    pipeline_name: Optional[str] = None
    status: str
    message: Optional[str] = None
    created_at: Optional[Any] = None

class JobDetailResponse(BaseModel):
    job_id: str
    pipeline_id: UUID
    pipeline_name: Optional[str] = None
    status: str
    message: Optional[str] = None
    created_at: Optional[Any] = None
    updated_at: Optional[Any] = None
    description: Optional[str] = None
    external_id: Optional[str] = None
    work_dir: Optional[str] = None
    output_dir: Optional[str] = None
    started_at: Optional[Any] = None
    completed_at: Optional[Any] = None

class JobList(BaseModel):
    jobs: List[JobResponse]

app = FastAPI(title="Nextflow Pipeline Platform API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(pipeline_router)

@app.get("/")
async def health_check():
    return {"status": "ok"}

# Authentication routes
@app.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    # Check if user already exists
    result = await db.execute(select(User).filter(User.username == form_data.username))
    db_user = result.scalars().first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(form_data.password)
    new_user = User(username=form_data.username, hashed_password=hashed_password)
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return new_user

@app.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    # Authenticate user
    result = await db.execute(select(User).filter(User.username == form_data.username))
    user = result.scalars().first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

# Job management routes
@app.post("/jobs", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def submit_job(
    job_data: JobCreate,
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    """
    Submit a new job for execution with the specified pipeline and parameters.
    """
    # Forward the request to the pipeline router's submit_pipeline_job endpoint
    from app.routers.pipeline_router import submit_pipeline_job, PipelineSubmission
    
    # Convert JobCreate to PipelineSubmission
    submission = PipelineSubmission(
        pipeline_id=job_data.pipeline_id,
        params=job_data.params,
        description=job_data.description
    )
    
    return await submit_pipeline_job(submission=submission, current_user=current_user, db=db)

@app.get("/jobs/{job_id}", response_model=JobDetailResponse)
async def get_job_status(
    job_id: str, 
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    """
    Get the status of a specific job.
    """
    # Forward the request to the pipeline router's get_pipeline_job endpoint
    from app.routers.pipeline_router import get_pipeline_job
    return await get_pipeline_job(job_id=job_id, current_user=current_user, db=db)

@app.get("/jobs", response_model=JobList)
async def list_jobs(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List all jobs for the current user.
    Admin users can see all jobs.
    """
    # Forward the request to the pipeline router's list_jobs endpoint
    from app.routers.pipeline_router import list_pipeline_jobs
    jobs = await list_pipeline_jobs(current_user=current_user, db=db)
    return {"jobs": jobs}
