#!/usr/bin/env python3
"""
Script to recreate database tables with the updated schema.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the parent directory to sys.path to access the app modules
parent_dir = str(Path(__file__).parent.parent)
sys.path.append(parent_dir)

from sqlalchemy.ext.asyncio import create_async_engine
from db.database import DATABASE_URL
from db.models import Base

async def recreate_db():
    """Recreate all database tables with the latest schema."""
    engine = create_async_engine(DATABASE_URL, echo=True)
    
    # Drop and recreate all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    print("Database tables recreated successfully.")

if __name__ == "__main__":
    asyncio.run(recreate_db())
