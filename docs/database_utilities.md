# Database Utilities

> ⏱️ **Time to read**: 5 minutes  
> 🗓️ **Last updated**: March 24, 2025

This document covers the database utilities available in the Nextflow Pipeline Platform, including the database reset utility for development and testing purposes.

## Table of Contents

- [Database Reset Utility](#database-reset-utility)
  - [Features](#features)
  - [Usage](#usage)
  - [Examples](#examples)
- [Database Migrations](#database-migrations)
- [Database Models](#database-models)
- [Best Practices](#best-practices)

## Database Reset Utility

The database reset utility is a tool designed to reset and optionally reseed the database with sample data, which is particularly useful during development and testing phases.

### Features

- **Safe Transaction Handling**: Uses SQLAlchemy transactions to ensure atomicity
- **Environment Separation**: Supports different databases for development, testing, and production
- **Clean Reset Process**: Drops all tables and recreates them from scratch using SQLAlchemy models
- **Optional Sample Data**: Adds sample data only when explicitly requested
- **Proper Error Handling**: Includes comprehensive logging and error handling
- **Security**: Includes confirmation prompts for destructive operations and additional safeguards for production

### Usage

The utility is accessible through a shell script wrapper in the `backend/scripts` directory:

```bash
./backend/scripts/reset_db.sh [environment] [options]
```

**Parameters:**
- `environment`: The target environment (`dev`, `test`, or `prod`)
- `options`: Additional flags to modify the reset behavior

**Available Options:**
- `--force`: Skip confirmation prompts
- `--with-sample-data`: Create sample data after reset

### Examples

**Reset Development Database (Interactive Mode)**
```bash
./backend/scripts/reset_db.sh dev
```

**Reset with Sample Data**
```bash
./backend/scripts/reset_db.sh dev --with-sample-data
```

**Force Reset Without Confirmation**
```bash
./backend/scripts/reset_db.sh dev --force
```

**Reset Test or Production Database**
```bash
./backend/scripts/reset_db.sh test
./backend/scripts/reset_db.sh prod  # Has additional safety confirmations
```

## Database Migrations

Database migrations are managed through Alembic:

```bash
# Run all pending migrations
cd backend
alembic upgrade head

# Create a new migration
alembic revision --autogenerate -m "Description of changes"
```

## Database Models

The platform uses SQLAlchemy ORM with three core models:

1. **User**:
   - Stores authentication data (username, hashed_password)
   - Includes role-based access control

2. **Pipeline**:
   - Represents Nextflow pipelines
   - Stores name, description, and configuration

3. **Job**:
   - Tracks pipeline execution instances
   - Contains foreign keys to User and Pipeline
   - Includes status tracking (pending, running, completed, failed)
   - Stores timestamps (creation, start, completion)
   - Contains execution parameters and output directory

## Best Practices

When working with the database utilities, follow these guidelines:

1. **Never reset production without explicit approval**
   - Production resets should be rare and carefully planned
   - Always backup production data before any reset

2. **Use different databases for different environments**
   - Keep development, testing, and production data separate
   - The reset utility enforces this separation automatically

3. **Prefer migrations over resets in stable environments**
   - Use Alembic migrations for schema changes in stable environments
   - Reserve complete resets for development and testing phases

4. **Be careful with sample data**
   - Sample data is useful for testing but should never leak into production
   - Verify that sample data meets your testing needs

5. **Follow the database operations best practices**:
   - Use transactions for atomicity
   - Implement proper error handling
   - Use connection pooling for performance
   - Apply proper validation before database operations
