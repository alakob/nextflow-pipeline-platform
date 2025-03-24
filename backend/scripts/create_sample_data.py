#!/usr/bin/env python3
"""
Script to create sample data in the database.
"""

import asyncio
import sys
import uuid
from pathlib import Path

# Add the parent directory to sys.path to access the app modules
parent_dir = str(Path(__file__).parent.parent)
sys.path.append(parent_dir)

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from db.database import DATABASE_URL
from db.models import User, Pipeline
from app.auth import get_password_hash

async def create_sample_data():
    """Create sample users and pipelines in the database."""
    engine = create_async_engine(DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Create admin user
        admin_user = User(
            username="admin",
            hashed_password=get_password_hash("admin"),
            role="admin"
        )
        session.add(admin_user)
        
        # Create test user if it doesn't exist
        test_user = User(
            username="test",
            hashed_password=get_password_hash("test"),
            role="user"
        )
        session.add(test_user)
        
        # Create sample pipelines
        rnaseq_pipeline = Pipeline(
            id=uuid.uuid4(),
            name="RNA-Seq Analysis",
            description="Pipeline for RNA sequencing analysis using DESeq2",
            nextflow_config="""
            process {
                executor = 'local'
                cpus = 4
                memory = '8 GB'
            }
            """
        )
        session.add(rnaseq_pipeline)
        
        variant_calling_pipeline = Pipeline(
            id=uuid.uuid4(),
            name="Variant Calling",
            description="Pipeline for variant calling using GATK",
            nextflow_config="""
            process {
                executor = 'local'
                cpus = 8
                memory = '16 GB'
            }
            """
        )
        session.add(variant_calling_pipeline)
        
        chip_seq_pipeline = Pipeline(
            id=uuid.uuid4(),
            name="ChIP-Seq Analysis",
            description="Pipeline for ChIP-Seq data processing and peak calling",
            nextflow_config="""
            process {
                executor = 'local'
                cpus = 4
                memory = '8 GB'
            }
            """
        )
        session.add(chip_seq_pipeline)
        
        await session.commit()
        
        print("Sample data created successfully:")
        print("- Admin user: admin/admin")
        print("- Test user: test/test")
        print("- 3 sample pipelines: RNA-Seq Analysis, Variant Calling, ChIP-Seq Analysis")

if __name__ == "__main__":
    asyncio.run(create_sample_data())
