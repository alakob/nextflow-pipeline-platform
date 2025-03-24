"""
Pytest configuration for FastAPI tests
"""
import os
import sys
import pytest
import asyncio
from datetime import datetime
from uuid import uuid4
import json
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

# Set TESTING environment variable
os.environ["TESTING"] = "true"

# Set up the path to import from project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the app and models
from app.main import app
from db.models import Base, User, Pipeline, Job
from app.auth import get_password_hash, create_access_token, get_current_user
from db.database import get_db

# Use a simple event loop for all tests
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()

# Test database engine
@pytest.fixture(scope="session")
def db_engine():
    """Create a SQLite in-memory database engine for testing."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        connect_args={"check_same_thread": False}
    )
    
    return engine

# Test database session
@pytest.fixture
async def db_session(db_engine):
    """Create a new database session for a test."""
    # Create tables
    async with db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    # Create a new session
    async_session = sessionmaker(
        db_engine, expire_on_commit=False, class_=AsyncSession
    )
    
    # Start a session
    async with async_session() as session:
        yield session
        await session.rollback()

# Test user
@pytest.fixture
async def test_user(db_session):
    """Create a test user."""
    user = User(
        id=uuid4(),
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("password123"),
        is_active=True,
        is_superuser=False,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    db_session.add(user)
    await db_session.commit()
    
    return user

# Test pipeline
@pytest.fixture
async def test_pipeline(db_session):
    """Create a test pipeline."""
    pipeline = Pipeline(
        id=uuid4(),
        name="Test Pipeline",
        description="A test pipeline",
        nextflow_config="workflow {}",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    db_session.add(pipeline)
    await db_session.commit()
    
    return pipeline

# Test job
@pytest.fixture
async def test_job(db_session, test_user, test_pipeline):
    """Create a test job."""
    job = Job(
        id=uuid4(),
        user_id=test_user.id,
        pipeline_id=test_pipeline.id,
        status="RUNNING",
        parameters=json.dumps({"test": "data"}),
        external_id="test-123",
        work_dir="/tmp/workdir",
        output_dir="/tmp/output",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    db_session.add(job)
    await db_session.commit()
    
    return job

# Test client with dependency overrides
@pytest.fixture
def client(test_user):
    """Create a test client with dependency overrides."""
    # Override get_db dependency
    async def override_get_db():
        # Create a new engine for each test
        engine = create_async_engine(
            "sqlite+aiosqlite:///:memory:",
            echo=False,
            connect_args={"check_same_thread": False}
        )
        
        # Create tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        # Create a new session
        async_session = sessionmaker(
            engine, expire_on_commit=False, class_=AsyncSession
        )
        
        # Start a session
        async with async_session() as session:
            yield session
    
    # Override get_current_user dependency
    async def override_get_current_user():
        return test_user
    
    # Set up dependency overrides
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    
    # Create test client
    with TestClient(app) as test_client:
        yield test_client
    
    # Clear dependency overrides
    app.dependency_overrides.clear()
