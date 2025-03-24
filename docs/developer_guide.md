# Developer Guide

> ⏱️ **Time to read**: 30 minutes  
> 🗓️ **Last updated**: March 24, 2025

This guide provides detailed information for developers working on the Nextflow Pipeline Platform, including architecture overview, development setup, code organization, and best practices.

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [System Components](#system-components)
- [Development Environment Setup](#development-environment-setup)
- [Code Organization](#code-organization)
- [Development Workflow](#development-workflow)
- [Testing](#testing)
- [Key Design Patterns](#key-design-patterns)
- [Performance Considerations](#performance-considerations)
- [Security Best Practices](#security-best-practices)
- [Contribution Guidelines](#contribution-guidelines)

## Architecture Overview

The Nextflow Pipeline Platform follows a modern, scalable architecture with clear separation of concerns. The system is designed to seamlessly orchestrate complex bioinformatics workflows on cloud infrastructure.

### High-Level Architecture

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│                  │     │                  │     │                  │
│   Frontend       │────▶│   Backend API    │────▶│   AWS Services   │
│   (React)        │     │   (FastAPI)      │     │                  │
│                  │◀────│                  │◀────│                  │
└──────────────────┘     └──────────────────┘     └──────────────────┘
                                   │                       ▲
                                   ▼                       │
                          ┌──────────────────┐     ┌──────────────────┐
                          │                  │     │                  │
                          │   Database       │     │   Nextflow       │
                          │   (PostgreSQL)   │     │   Engine         │
                          │                  │     │                  │
                          └──────────────────┘     └──────────────────┘
```

### Key Design Principles

1. **Microservices Architecture**: Components are loosely coupled and can be developed, deployed, and scaled independently.

2. **API-First Design**: All functionality is exposed through a well-defined API, enabling both UI and programmatic access.

3. **Stateless Backend**: The backend API is stateless, with session state stored in tokens and data persisted in the database.

4. **Event-Driven Processing**: Asynchronous processing for long-running tasks using event queues.

5. **Infrastructure as Code**: All cloud resources are defined and managed through code (Terraform).

## System Components

### Frontend

- **Technology**: React.js
- **Purpose**: Provides the user interface for pipeline management, job submission, and monitoring
- **Key Features**:
  - Responsive design
  - Real-time updates via WebSockets
  - Interactive data visualization
  - Progressive loading for large datasets

### Backend API

- **Technology**: FastAPI (Python)
- **Purpose**: Exposes RESTful endpoints for all platform functionality
- **Key Features**:
  - Asynchronous request handling
  - Automatic OpenAPI documentation
  - JWT-based authentication
  - Role-based access control
  - API versioning

### Database

- **Technology**: PostgreSQL
- **Purpose**: Stores user data, pipeline metadata, job configurations, and execution status
- **Schema Overview**:
  - Users and authentication
  - Pipelines and configurations
  - Jobs and execution history
  - Audit logs

### Nextflow Engine

- **Technology**: Nextflow
- **Purpose**: Executes bioinformatics workflows
- **Integration Points**:
  - Process execution on AWS Batch
  - Data storage on S3
  - Monitoring and logging

### AWS Services Integration

- **AWS Batch**: Executes containerized workflow steps
- **S3**: Stores input data, intermediate files, and results
- **IAM**: Manages access permissions
- **CloudWatch**: Monitors resources and logs
- **ECR**: Stores pipeline containers

## Development Environment Setup

### Prerequisites

- Python 3.10+
- Node.js 16+
- Docker
- AWS CLI
- PostgreSQL 13+
- Terraform 1.0+

### Setup Script

Use our automated setup script for a quick development environment:

```bash
# Clone the repository
git clone https://github.com/your-org/nextflow-pipeline-platform.git
cd nextflow-pipeline-platform

# Run the setup script
./scripts/setup_dev.sh
```

### Manual Setup

If you prefer a manual setup:

1. **Backend Setup**:

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Configure your environment variables
```

2. **Database Setup**:

```bash
createdb nextflow_platform_dev
cd backend
alembic upgrade head
```

3. **Frontend Setup**:

```bash
cd frontend
npm install
cp .env.example .env  # Configure your environment variables
```

### Running the Development Environment

1. **Start the Backend**:

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

2. **Start the Frontend**:

```bash
cd frontend
npm start
```

## Code Organization

### Directory Structure

```
├── backend/                # FastAPI application
│   ├── app/                # Application code
│   │   ├── api/            # API routes
│   │   ├── core/           # Core functionality
│   │   ├── db/             # Database models and utilities
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic
│   │   └── main.py         # Application entry point
│   ├── tests/              # Backend tests
│   └── requirements.txt    # Python dependencies
├── frontend/               # React application
│   ├── public/             # Static assets
│   ├── src/                # Source code
│   │   ├── components/     # React components
│   │   ├── hooks/          # Custom React hooks
│   │   ├── pages/          # Page components
│   │   ├── services/       # API client and utilities
│   │   └── App.js          # Application entry point
│   └── package.json        # NPM dependencies
├── pipeline/               # Nextflow pipelines
│   ├── modules/            # Pipeline modules
│   ├── conf/               # Configuration files
│   └── bin/                # Utility scripts
├── infra/                  # Terraform configurations
│   ├── modules/            # Terraform modules
│   ├── environments/       # Environment-specific configs
│   └── main.tf             # Main Terraform entry point
├── scripts/                # Utility scripts
├── docs/                   # Documentation
└── tests/                  # Integration tests
```

### Backend Structure

The backend follows a layered architecture:

1. **API Layer** (`app/api/`): Route definitions and request handling
2. **Schema Layer** (`app/schemas/`): Data validation and serialization
3. **Service Layer** (`app/services/`): Business logic
4. **Data Access Layer** (`app/db/`): Database models and queries

### Frontend Structure

The frontend follows a component-based architecture:

1. **Pages**: Top-level route components
2. **Components**: Reusable UI elements
3. **Hooks**: Custom React hooks for shared logic
4. **Services**: API client and utilities
5. **Store**: State management with Redux/Context

## Development Workflow

### Git Workflow

We follow a feature branch workflow:

1. Create a feature branch from `dev`: `git checkout -b feature/new-feature`
2. Make your changes
3. Write tests
4. Submit a pull request to `dev`

### Continuous Integration

All pull requests trigger CI checks:

1. Linting and code style checks
2. Unit tests
3. Integration tests
4. Build verification

### Development Process

1. **Issue Tracking**: All work is tracked in GitHub Issues
2. **Feature Planning**: Features are planned and designed before implementation
3. **Implementation**: Code is written, tested, and documented
4. **Review**: Code is reviewed by at least one other developer
5. **Testing**: All code is tested before merging
6. **Deployment**: Changes are deployed to staging before production

## Testing

### Testing Strategy

We follow a comprehensive testing strategy:

1. **Unit Tests**: Test individual functions and components
2. **Integration Tests**: Test the interaction between components
3. **API Tests**: Test the API endpoints
4. **End-to-End Tests**: Test the entire application flow

### Backend Testing

```bash
cd backend
python -m pytest
```

Key backend testing tools:
- pytest: Test runner
- pytest-asyncio: Testing async functions
- httpx: Testing HTTP endpoints

### Frontend Testing

```bash
cd frontend
npm test
```

Key frontend testing tools:
- Jest: Test runner
- React Testing Library: Testing React components
- MSW: Mocking API requests

### Integration Testing

```bash
cd tests
./run_integration_tests.sh
```

## Key Design Patterns

### Backend Patterns

1. **Repository Pattern**: Database access is abstracted through repositories
2. **Dependency Injection**: Dependencies are injected through FastAPI's dependency system
3. **Factory Pattern**: Used for creating complex objects
4. **Strategy Pattern**: Used for different pipeline execution strategies

Example repository pattern:

```python
# Repository pattern example
class JobRepository:
    def __init__(self, db_session: Session):
        self.db_session = db_session
    
    async def get_by_id(self, job_id: str) -> Optional[Job]:
        return await self.db_session.query(Job).filter(Job.id == job_id).first()
    
    async def create(self, job: JobCreate) -> Job:
        db_job = Job(**job.dict())
        self.db_session.add(db_job)
        await self.db_session.commit()
        await self.db_session.refresh(db_job)
        return db_job
```

### Frontend Patterns

1. **Container/Presenter Pattern**: Separation of data fetching and presentation
2. **Custom Hooks**: Reusable logic encapsulated in hooks
3. **Context API**: For shared state management
4. **Render Props**: For component composition

Example custom hook:

```javascript
// Custom hook example
function useJob(jobId) {
  const [job, setJob] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchJob() {
      try {
        setLoading(true);
        const response = await api.getJob(jobId);
        setJob(response.data);
      } catch (err) {
        setError(err);
      } finally {
        setLoading(false);
      }
    }
    
    fetchJob();
    
    // Set up polling for job status updates
    const interval = setInterval(fetchJob, 5000);
    return () => clearInterval(interval);
  }, [jobId]);

  return { job, loading, error };
}
```

## Performance Considerations

### Backend Performance

1. **Async Processing**: Use async/await for I/O-bound operations
2. **Connection Pooling**: Optimize database connections
3. **Query Optimization**: Use efficient database queries
4. **Caching**: Cache frequently accessed data
5. **Task Queues**: Offload long-running tasks to background workers

Example of efficient async handling:

```python
@router.get("/jobs/{job_id}")
async def get_job(
    job_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    job = await db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Check permissions
    if job.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to access this job")
    
    return job
```

### Frontend Performance

1. **Code Splitting**: Split code by route for faster loading
2. **Lazy Loading**: Load components only when needed
3. **Memoization**: Memoize expensive computations
4. **Virtualization**: Virtualize long lists for better performance
5. **Progressive Loading**: Load data progressively for better UX

## Security Best Practices

### Authentication and Authorization

1. **JWT Security**: Use short-lived tokens and refresh tokens
2. **Password Storage**: Hash passwords with bcrypt
3. **Role-Based Access Control**: Control access based on user roles
4. **Rate Limiting**: Prevent brute-force attacks

### API Security

1. **Input Validation**: Validate all input data
2. **CORS Configuration**: Configure CORS correctly
3. **Content Security Policy**: Implement CSP headers
4. **HTTPS Only**: Enforce HTTPS for all communications

### Data Security

1. **Data Encryption**: Encrypt sensitive data
2. **Least Privilege**: Follow the principle of least privilege
3. **Audit Logging**: Log all sensitive operations
4. **Secure File Handling**: Handle uploaded files securely

## Contribution Guidelines

### Code Style

- Backend: Follow PEP 8 style guide
- Frontend: Follow Airbnb JavaScript style guide

### Documentation

- Document all public functions, classes, and modules
- Keep documentation up-to-date with code changes
- Use type hints in Python code

### Pull Request Process

1. Ensure code passes all tests
2. Update documentation if needed
3. Request review from relevant team members
4. Address all review comments

### Release Process

1. Create a release branch from `dev`
2. Run final tests
3. Update version numbers
4. Merge to `main`
5. Tag the release

## Architectural Decision Records

We maintain architectural decision records (ADRs) to document important architectural decisions:

- [ADR-001: Choice of FastAPI for Backend](../docs/adr/adr-001-fastapi.md)
- [ADR-002: Database Schema Design](../docs/adr/adr-002-database-schema.md)
- [ADR-003: Authentication Strategy](../docs/adr/adr-003-authentication.md)

---

**Next Steps**:
- [API Documentation](api.md)
- [Deployment Guide](deployment.md)
- [Contributing Guide](contributing.md)
