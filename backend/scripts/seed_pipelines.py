#!/usr/bin/env python3
"""
Script to seed the database with initial pipeline data.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the parent directory to sys.path to access the app modules
parent_dir = str(Path(__file__).parent.parent)
sys.path.append(parent_dir)

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.database import AsyncSessionLocal, engine
from db.models import Base, Pipeline

# Sample pipeline definitions
SAMPLE_PIPELINES = [
    {
        "name": "RNA-Seq Analysis",
        "description": "Pipeline for RNA sequencing data analysis, including quality control, alignment, and differential expression analysis.",
        "nextflow_config": """
        params {
            reads = 's3://sample-data/reads/*.fastq.gz'
            genome = 's3://sample-data/reference/genome.fasta'
            annotation = 's3://sample-data/reference/genes.gtf'
            outdir = 's3://output/rnaseq'
        }
        
        profiles {
            aws {
                process.executor = 'awsbatch'
                process.queue = 'nextflow-pipeline-queue'
                aws.region = 'eu-north-1'
            }
        }
        """
    },
    {
        "name": "Variant Calling",
        "description": "Pipeline for identifying genomic variants from DNA sequencing data, including alignment, variant calling, and annotation.",
        "nextflow_config": """
        params {
            reads = 's3://sample-data/reads/*.fastq.gz'
            reference = 's3://sample-data/reference/genome.fasta'
            outdir = 's3://output/variants'
        }
        
        profiles {
            aws {
                process.executor = 'awsbatch'
                process.queue = 'nextflow-pipeline-queue'
                aws.region = 'eu-north-1'
            }
        }
        """
    },
    {
        "name": "Metagenomic Analysis",
        "description": "Pipeline for analyzing metagenomic sequencing data to characterize microbial communities.",
        "nextflow_config": """
        params {
            reads = 's3://sample-data/reads/*.fastq.gz'
            database = 's3://sample-data/reference/metagenomic_db'
            outdir = 's3://output/metagenomics'
        }
        
        profiles {
            aws {
                process.executor = 'awsbatch'
                process.queue = 'nextflow-pipeline-queue'
                aws.region = 'eu-north-1'
            }
        }
        """
    }
]

async def seed_pipelines():
    """Seed the database with sample pipelines."""
    async with engine.begin() as conn:
        # Create tables if they don't exist
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSessionLocal() as session:
        # Check if we already have pipelines
        result = await session.execute(select(Pipeline))
        existing_pipelines = result.scalars().all()
        
        if existing_pipelines:
            print(f"Database already contains {len(existing_pipelines)} pipelines.")
            return
        
        # Add sample pipelines
        for pipeline_data in SAMPLE_PIPELINES:
            pipeline = Pipeline(**pipeline_data)
            session.add(pipeline)
        
        await session.commit()
        print(f"Added {len(SAMPLE_PIPELINES)} sample pipelines to the database.")

if __name__ == "__main__":
    asyncio.run(seed_pipelines())
