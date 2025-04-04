"""create tables

Revision ID: 7ed1526d0ab1
Revises: 
Create Date: 2025-03-23 21:26:48.814752

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import Column, String, ForeignKey, DateTime, Text
from datetime import datetime


# revision identifiers, used by Alembic.
revision: str = '7ed1526d0ab1'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create all tables."""
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(36), primary_key=True, index=True),
        sa.Column('username', sa.String(), nullable=False, unique=True, index=True),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('role', sa.String(), nullable=False, server_default='user'),
    )

    # Create pipelines table
    op.create_table(
        'pipelines',
        sa.Column('id', sa.String(36), primary_key=True, index=True),
        sa.Column('name', sa.String(), nullable=False, unique=True),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('nextflow_config', sa.Text(), nullable=True),
    )

    # Create jobs table
    op.create_table(
        'jobs',
        sa.Column('id', sa.String(36), primary_key=True, index=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('pipeline_id', sa.String(36), sa.ForeignKey('pipelines.id'), nullable=False),
        sa.Column('status', sa.String(), nullable=False, server_default='pending'),
        sa.Column('parameters', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()'), onupdate=sa.text('now()')),
        sa.Column('external_id', sa.String(), nullable=True),
        sa.Column('work_dir', sa.String(), nullable=True),
        sa.Column('output_dir', sa.String(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('description', sa.String(), nullable=True),
    )


def downgrade() -> None:
    """Drop all tables in reverse order."""
    op.drop_table('jobs')
    op.drop_table('pipelines')
    op.drop_table('users')
