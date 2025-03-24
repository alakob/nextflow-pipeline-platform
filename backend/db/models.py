from sqlalchemy import Column, String, ForeignKey, DateTime, Text, TypeDecorator, JSON
from sqlalchemy.orm import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

# Custom UUID type that works with SQLite
class UUIDString(TypeDecorator):
    """Custom UUID type for SQLite that stores UUIDs as strings"""
    impl = String
    cache_ok = True

    def __init__(self, length=36, **kwargs):
        super().__init__(length=length, **kwargs)

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, uuid.UUID):
            return str(value)
        return value

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if not isinstance(value, uuid.UUID) and value != '':
            try:
                return uuid.UUID(value)
            except (ValueError, TypeError):
                return value
        return value

class User(Base):
    __tablename__ = "users"
    id = Column(UUIDString, primary_key=True, default=uuid.uuid4, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="user")

class Pipeline(Base):
    __tablename__ = "pipelines"
    id = Column(UUIDString, primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, unique=True)
    description = Column(String)
    nextflow_config = Column(Text)

class Job(Base):
    __tablename__ = "jobs"
    id = Column(String, primary_key=True, index=True)  # Using String for custom job IDs
    user_id = Column(UUIDString, ForeignKey("users.id"))
    pipeline_id = Column(UUIDString, ForeignKey("pipelines.id"))
    status = Column(String, default="PENDING")
    params = Column(JSON, default={})  # Using JSON column for structured parameters
    message = Column(String)  # For status messages
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    # Add missing fields referenced in the router
    external_id = Column(String)
    work_dir = Column(String)
    output_dir = Column(String)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    description = Column(String)
