"""
Script to create test database schema and initial data for testing
"""
import asyncio
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession

# Import models
from db.database import Base
from db.models import User, Pipeline, Job
from app.auth import get_password_hash


async def setup_test_db():
    """Create test database and seed with initial data"""
    # Use in-memory SQLite for testing
    DATABASE_URL = "sqlite+aiosqlite:///:memory:"
    
    # Create engine and tables
    engine = create_async_engine(DATABASE_URL, echo=True)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session
    async_session_maker = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )
    
    # Seed initial data
    async with async_session_maker() as session:
        # Create test user
        test_user = User(
            username="testuser",
            hashed_password=get_password_hash("password123"),
            is_admin=False
        )
        session.add(test_user)
        
        # Create admin user
        admin_user = User(
            username="admin",
            hashed_password=get_password_hash("adminpassword"),
            is_admin=True
        )
        session.add(admin_user)
        
        # Create test pipeline
        test_pipeline = Pipeline(
            name="Test Pipeline",
            description="A pipeline for testing",
            config={"script": "test.nf", "container": "nfcore/rnaseq:latest"}
        )
        session.add(test_pipeline)
        
        await session.commit()
        
        # Refresh to get IDs
        await session.refresh(test_user)
        await session.refresh(test_pipeline)
        
        # Create test job
        test_job = Job(
            user_id=test_user.id,
            pipeline_id=test_pipeline.id,
            status="queued",
            params={"sample": "test_sample"},
            description="Test job"
        )
        session.add(test_job)
        
        await session.commit()
    
    print("Test database setup complete!")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(setup_test_db())
