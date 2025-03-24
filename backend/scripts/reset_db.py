#!/usr/bin/env python
"""
Database Reset Utility

This script completely resets the database by dropping all tables
and recreating them from scratch using the defined SQLAlchemy models.

Usage:
    python reset_db.py [--force] [--with-sample-data]

Options:
    --force             Skip confirmation prompt
    --with-sample-data  Include sample data after reset
"""

import os
import sys
import asyncio
import logging
import argparse
from datetime import datetime
import uuid
from typing import Optional, List

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import database components
from db.database import engine, AsyncSessionLocal, Base
from db.models import User, Pipeline, Job
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("db_reset")

async def drop_all_tables(force: bool = False) -> bool:
    """
    Drop all tables in the database.
    
    Args:
        force: If True, skip confirmation
        
    Returns:
        bool: True if tables were dropped, False otherwise
    """
    if not force:
        confirm = input("⚠️  WARNING: This will DELETE ALL DATA in the database. Continue? [y/N]: ")
        if confirm.lower() not in ['y', 'yes']:
            logger.info("Database reset cancelled by user.")
            return False
    
    logger.info("Dropping all tables...")
    
    # Use a transaction to ensure atomicity
    async with engine.begin() as conn:
        try:
            # Drop all tables from metadata
            await conn.run_sync(Base.metadata.drop_all)
            logger.info("All tables dropped successfully.")
            return True
        except Exception as e:
            logger.error(f"Error dropping tables: {str(e)}")
            return False

async def create_all_tables() -> bool:
    """
    Create all tables defined in SQLAlchemy models.
    
    Returns:
        bool: True if tables were created, False otherwise
    """
    logger.info("Creating all tables...")
    
    # Use a transaction to ensure atomicity
    async with engine.begin() as conn:
        try:
            # Create all tables from metadata
            await conn.run_sync(Base.metadata.create_all)
            logger.info("All tables created successfully.")
            return True
        except Exception as e:
            logger.error(f"Error creating tables: {str(e)}")
            return False

async def create_sample_data(db: AsyncSession) -> bool:
    """
    Create sample data for testing purposes.
    
    Args:
        db: An active database session
        
    Returns:
        bool: True if sample data was created, False otherwise
    """
    logger.info("Creating sample data...")
    
    try:
        # Create a test admin user with hashed password 'admin'
        admin_user = User(
            id=uuid.uuid4(),
            username="admin",
            hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # 'password'
            role="admin"
        )
        
        # Create a test regular user
        test_user = User(
            id=uuid.uuid4(),
            username="testuser",
            hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # 'password'
            role="user"
        )
        
        # Create sample pipelines
        rnaseq_pipeline = Pipeline(
            id=uuid.uuid4(),
            name="RNA-Seq Analysis",
            description="Pipeline for analyzing RNA sequencing data",
            nextflow_config="includeConfig 'modules/rnaseq.config'"
        )
        
        variant_pipeline = Pipeline(
            id=uuid.uuid4(),
            name="Variant Calling",
            description="Germline variant calling with GATK",
            nextflow_config="includeConfig 'modules/variant.config'"
        )
        
        # Add all entities to session
        db.add_all([admin_user, test_user, rnaseq_pipeline, variant_pipeline])
        
        # Sample job
        sample_job = Job(
            id=f"JOB_{uuid.uuid4().hex[:8]}",
            user_id=admin_user.id,
            pipeline_id=rnaseq_pipeline.id,
            status="COMPLETED",
            params={"sample_name": "test_sample", "genome": "hg38"},
            message="Job completed successfully",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            external_id="workflow_12345",
            work_dir="/tmp/nextflow/work",
            output_dir="/data/results/job_12345",
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            description="Test job for RNA-Seq analysis"
        )
        
        db.add(sample_job)
        
        # Commit the transaction
        await db.commit()
        
        logger.info(f"Created admin user: {admin_user.username}")
        logger.info(f"Created test user: {test_user.username}")
        logger.info(f"Created pipelines: {rnaseq_pipeline.name}, {variant_pipeline.name}")
        logger.info(f"Created sample job: {sample_job.id}")
        
        return True
    except Exception as e:
        # Rollback in case of error
        await db.rollback()
        logger.error(f"Error creating sample data: {str(e)}")
        return False

async def reset_database(force: bool = False, with_sample_data: bool = False) -> bool:
    """
    Reset the database by dropping all tables and recreating them.
    
    Args:
        force: If True, skip confirmation
        with_sample_data: If True, create sample data after reset
        
    Returns:
        bool: True if reset was successful, False otherwise
    """
    # Start by dropping all tables
    if not await drop_all_tables(force):
        return False
    
    # Create all tables from SQLAlchemy models
    if not await create_all_tables():
        return False
    
    # Create sample data if requested
    if with_sample_data:
        async with AsyncSessionLocal() as session:
            if not await create_sample_data(session):
                return False
    
    logger.info("Database reset completed successfully! 🎉")
    return True

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Reset the database")
    parser.add_argument("--force", action="store_true", help="Skip confirmation prompt")
    parser.add_argument("--with-sample-data", action="store_true", help="Include sample data after reset")
    return parser.parse_args()

async def main():
    """Main entry point for the script."""
    args = parse_args()
    
    # Display database connection info
    db_url = os.environ.get("DATABASE_URL", "Default connection string")
    # Hide credentials in logs
    safe_db_url = db_url.replace("://", "://***:***@") if "://" in db_url else db_url
    logger.info(f"Database: {safe_db_url}")
    
    success = await reset_database(args.force, args.with_sample_data)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())
