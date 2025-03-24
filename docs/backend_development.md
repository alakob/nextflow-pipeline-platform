# Backend Development Guide

This guide provides detailed information for developers working on the Nextflow Pipeline Platform backend.

## Architecture Overview

The backend is built using [FastAPI](https://fastapi.tiangolo.com/), a modern, high-performance web framework for building APIs with Python based on standard Python type hints. It follows a functional programming approach with clear separation of concerns.

## Project Structure

```
backend/
├── alembic/            # Database migration scripts
├── app/                # Application code
│   ├── routers/        # API endpoint definitions
│   │   ├── __init__.py
│   │   └── pipeline_router.py
│   ├── services/       # Business logic implementations
│   │   ├── __init__.py
│   │   └── pipeline_service.py
│   ├── auth.py         # Authentication and authorization
│   └── main.py         # Application entry point
├── db/                 # Database related code
│   ├── database.py     # Database connection management
│   └── models.py       # SQLAlchemy ORM models
├── tests/              # Test suite
│   ├── conftest.py     # Test fixtures and configuration
│   └── test_routes.py  # API endpoint tests
├── .env                # Environment configuration
├── .env.example        # Example environment configuration
└── requirements.txt    # Python dependencies
```

## Development Workflow

### Setting Up the Development Environment

The recommended approach is to use the automated setup script which handles all configuration steps:

```bash
# From project root directory
./scripts/setup_dev.sh
```

For running just the backend service in development mode:

```bash
./scripts/setup_dev.sh --start-backend-dev
```

### Manual Setup (Alternative)

If you prefer to set up manually:

1. Ensure PostgreSQL is running via Docker Compose:
   ```bash
   # From project root directory
   docker-compose up -d postgres
   ```

2. Create a virtual environment:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration, ensuring DATABASE_URL points to the Docker PostgreSQL instance:
   # DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/nextflow_platform
   ```

5. Initialize the database:
   ```bash
   alembic upgrade head
   ```

### Running the Development Server

Start the FastAPI development server:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at http://localhost:8000 with interactive documentation at http://localhost:8000/docs.

### Database Connectivity

The backend uses SQLAlchemy with an async PostgreSQL adapter. The connection is configured through the `DATABASE_URL` environment variable:

```
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/nextflow_platform
```

Key components:
- `postgresql+asyncpg`: The SQLAlchemy async driver for PostgreSQL
- `postgres:postgres`: Database username:password
- `localhost:5432`: Host and port for the PostgreSQL server
- `nextflow_platform`: Database name

The Docker Compose setup automatically creates and manages this database container.

## Key Components

### Routers

Routers define the API endpoints and handle HTTP requests. They should:

- Use standard HTTP methods (GET, POST, PUT, DELETE) appropriately
- Include proper input validation using Pydantic models
- Handle authentication and authorization
- Delegate business logic to services
- Return properly structured responses

Example:

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import get_db
from app.auth import get_current_user
from db.models import User

router = APIRouter(prefix="/pipelines", tags=["pipelines"])

@router.get("/")
async def list_pipelines(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Implementation here
    pass
```

### Services

Services contain the business logic of the application. They should:

- Be independent of HTTP-specific concerns
- Implement the core functionality of the application
- Interface with the database through SQLAlchemy models
- Be testable in isolation

Example:

```python
async def run_pipeline(
    pipeline_id: UUID,
    user_id: UUID,
    params: Dict[str, Any]
) -> Dict[str, Any]:
    # Implementation here
    pass
```

### Database Models

Models define the database schema using SQLAlchemy ORM. They should:

- Use appropriate column types
- Define relationships between tables
- Include sensible default values and constraints
- Follow standard naming conventions

Example:

```python
class Job(Base):
    __tablename__ = "jobs"
    id = Column(UUIDString, primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUIDString, ForeignKey("users.id"))
    pipeline_id = Column(UUIDString, ForeignKey("pipelines.id"))
    status = Column(String, default="pending")
    # More fields...
```

### Authentication

The application uses JWT-based authentication:

- JWTs are generated on login and verified on protected routes
- Password hashing uses BCrypt through Passlib
- Authentication middleware protects routes as needed
- Role-based access control is implemented for admin functions

## Testing

### Running Tests

Run the test suite:

```bash
pytest
```

Run tests with coverage:

```bash
pytest --cov=app
```

### Writing Tests

The project uses pytest for testing. Tests should:

- Use fixtures defined in conftest.py
- Test endpoints through the FastAPI TestClient
- Mock external services (like Nextflow execution)
- Include both positive and negative test cases
- Test authentication and authorization

Example:

```python
def test_list_pipelines(client, test_pipeline):
    """Test listing available pipelines."""
    with patch("app.routers.pipeline_router.get_pipelines") as mock_get_pipelines:
        # Mock the pipeline listing
        mock_get_pipelines.return_value = AsyncMock(return_value=[
            {
                "id": str(test_pipeline.id),
                "name": test_pipeline.name,
                "description": test_pipeline.description,
                "created_at": test_pipeline.created_at.isoformat()
            }
        ])
        
        # Make the request
        response = client.get("/pipelines")
        
        # Check response
        assert response.status_code == status.HTTP_200_OK
        pipelines = response.json()
        assert isinstance(pipelines, list)
        assert len(pipelines) == 1
        assert pipelines[0]["id"] == str(test_pipeline.id)
```

## Database Migrations

The project uses Alembic for database migrations:

- Generate a new migration after model changes:
  ```bash
  alembic revision --autogenerate -m "Description of changes"
  ```

- Apply migrations:
  ```bash
  alembic upgrade head
  ```

## Best Practices

### Code Style

- Follow PEP 8 style guidelines
- Use type hints for all function signatures
- Write docstrings for all functions and classes
- Use async/await for database operations and external services
- Keep functions small and focused on a single responsibility

### API Design

- Use RESTful principles
- Versioning through URL paths (e.g., /api/v1/resource)
- Consistent error responses
- Proper use of HTTP status codes
- Input validation with Pydantic models

### Security

- Store secrets in environment variables, never in code
- Always hash passwords, never store plaintext
- Validate all user input
- Implement proper role-based access control
- Use HTTPS in production
- Include appropriate security headers

## Troubleshooting

### Common Issues

- **Database connection errors**: Check your database URL and credentials
- **Migration errors**: Ensure your migration scripts are up to date
- **Authentication failures**: Verify your JWT secret key and token expiration
- **Slow performance**: Check for N+1 query issues or missing database indexes

### Debugging

- Use FastAPI's debug mode for detailed error information
- Check logs for error details
- Use pytest's `-v` flag for verbose test output
- Insert breakpoints with `import pdb; pdb.set_trace()`

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [JWT Documentation](https://jwt.io/)
