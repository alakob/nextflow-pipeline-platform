from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, Any

from db.database import get_db
from db.models import User, Job
from app.auth import get_password_hash, verify_password, create_access_token, get_current_user
from app.routers import pipeline_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(pipeline_router.router)

@app.get("/")
async def health_check():
    return {"status": "ok"}

# Authentication routes
@app.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(
    username: str, 
    password: str,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    # Check if user already exists
    result = await db.execute(select(User).filter(User.username == username))
    db_user = result.scalars().first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(password)
    new_user = User(username=username, hashed_password=hashed_password)
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return {"username": new_user.username, "id": new_user.id}

@app.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, str]:
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
    access_token = create_access_token(data={"sub": user.id})
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_user)) -> Dict[str, Any]:
    return {
        "id": current_user.id,
        "username": current_user.username,
        "role": current_user.role
    }

# Job management routes
@app.post("/jobs", status_code=status.HTTP_201_CREATED)
async def submit_job(
    pipeline_id: int, 
    parameters: str, 
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Submit a new job for execution with the specified pipeline and parameters.
    """
    # Create new job
    job = Job(
        user_id=current_user.id,
        pipeline_id=pipeline_id,
        parameters=parameters
    )
    
    db.add(job)
    await db.commit()
    await db.refresh(job)
    
    return {
        "job_id": job.id,
        "status": job.status,
        "created_at": job.created_at
    }

@app.get("/jobs/{job_id}")
async def get_job_status(
    job_id: int, 
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get the status of a specific job.
    """
    result = await db.execute(select(Job).filter(Job.id == job_id))
    job = result.scalars().first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Check if user has access to this job
    if job.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this job"
        )
    
    return {
        "job_id": job.id,
        "status": job.status,
        "pipeline_id": job.pipeline_id,
        "parameters": job.parameters,
        "created_at": job.created_at,
        "updated_at": job.updated_at
    }

@app.get("/jobs")
async def list_jobs(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    List all jobs for the current user or all jobs for admin users.
    """
    if current_user.role == "admin":
        result = await db.execute(select(Job))
        jobs = result.scalars().all()
    else:
        result = await db.execute(select(Job).filter(Job.user_id == current_user.id))
        jobs = result.scalars().all()
    
    return {
        "jobs": [
            {
                "job_id": job.id,
                "status": job.status,
                "pipeline_id": job.pipeline_id,
                "created_at": job.created_at
            } 
            for job in jobs
        ]
    }
