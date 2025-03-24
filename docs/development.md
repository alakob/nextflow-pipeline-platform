# Development Guide

This guide provides general development guidelines and best practices for contributing to the Nextflow Pipeline Platform.

## Development Philosophy

The Nextflow Pipeline Platform follows these core development principles:

1. **Simplicity** - Prefer simple solutions over complex ones
2. **Modularity** - Build small, reusable components
3. **Clarity** - Write clean, readable code with descriptive naming
4. **Testability** - Design code for easy testing
5. **Performance** - Optimize for speed and resource efficiency

## Environment Setup

### Automated Setup Script

The project includes a comprehensive setup script (`scripts/setup_dev.sh`) that automates the development environment configuration process. This is the recommended approach for most developers.

```bash
# Basic setup (environment configuration only)
./scripts/setup_dev.sh
```

#### Setup Script Features

The setup script handles the following tasks:

1. **Environment Validation** - Checks for required dependencies
2. **Database Setup** - Starts PostgreSQL using Docker Compose
3. **Backend Configuration**
   - Creates Python virtual environment
   - Installs required packages
   - Sets up environment variables
   - Runs database migrations
4. **Frontend Configuration**
   - Installs Node.js dependencies
   - Sets up environment variables
5. **Pipeline Setup** - Creates necessary directories

#### Starting Services

The setup script provides several command-line options:

```bash
# Start all services (frontend, backend, PostgreSQL)
./scripts/setup_dev.sh --start

# Start all services in detached mode (background)
./scripts/setup_dev.sh --start-detached

# Start only backend with PostgreSQL
./scripts/setup_dev.sh --start-backend

# Start only frontend
./scripts/setup_dev.sh --start-frontend

# Start backend in development mode with hot-reloading
./scripts/setup_dev.sh --start-backend-dev

# Start frontend in development mode
./scripts/setup_dev.sh --start-frontend-dev

# Run the test suite
./scripts/setup_dev.sh --test
```

#### Docker-Based Database

The platform uses a Docker-based PostgreSQL database for development, eliminating the need for a local PostgreSQL installation:

- PostgreSQL runs in a Docker container
- Data is persisted in a Docker volume
- Environment variables are configured automatically
- Database migrations are run during setup

### Manual Development Environment

If you prefer to set up components individually, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/alakob/nextflow-pipeline-platform.git
   cd nextflow-pipeline-platform
   ```

2. Start the PostgreSQL container:
   ```bash
   docker-compose up -d postgres
   ```

3. Set up separate environments for each component:
   - [Backend Setup](backend_development.md)
   - [Frontend Setup](frontend_development.md)
   - [Pipeline Setup](pipeline_development.md)

4. Configure local environment variables:
   ```bash
   # Backend
   cd backend
   cp .env.example .env
   # Edit .env with development settings
   
   # Frontend
   cd ../frontend
   cp .env.example .env
   # Edit .env with development settings
   ```

## Development Workflow

### Git Workflow

1. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make changes and commit with descriptive messages:
   ```bash
   git add .
   git commit -m "Add feature X that does Y"
   ```

3. Push changes and create a pull request:
   ```bash
   git push origin feature/your-feature-name
   ```

4. Request code review from team members
5. Address review feedback
6. Merge to main branch when approved

### Environment Separation

The platform strictly separates the following environments:

1. **Development (dev)** - For active development work
   - Local database
   - Mocked AWS services when possible
   - Debug logs enabled

2. **Testing (test)** - For automated testing
   - Isolated test database
   - Test-specific configurations
   - Used by CI/CD pipelines

3. **Production (prod)** - For live deployed system
   - Production database
   - Full AWS integration
   - Performance optimized
   - Detailed error logging

Never use production resources for development or testing.

## Code Organization

### Directory Structure

The project maintains a clean separation of concerns:

```
/
├── backend/                # FastAPI Python backend
├── frontend/               # React frontend
├── pipeline/               # Nextflow pipeline definitions
├── infra/                  # Terraform infrastructure code
├── docs/                   # Documentation
└── tests/                  # End-to-end tests
```

### Coding Style

#### Python (Backend)

- Follow PEP 8 style guidelines
- Use type hints for function signatures
- Use functional programming patterns when appropriate
- Keep functions small and focused
- Use descriptive variable names with auxiliary verbs (e.g., `is_active`, `has_permission`)
- Use `async`/`await` for I/O operations

#### JavaScript/TypeScript (Frontend)

- Follow ESLint rules defined in the project
- Use functional components with React hooks
- Use TypeScript interfaces for type definitions
- Implement proper error boundaries
- Follow the container/component pattern

#### Infrastructure as Code

- Use Terraform modules for reusable components
- Separate state files per environment
- Use variables for configuration
- Document all resource configurations

## Testing Strategy

### Backend Testing

- Unit tests for individual functions
- Integration tests for API endpoints
- Mock external services (AWS, etc.)
- Use pytest fixtures for test setup
- Measure code coverage

### Frontend Testing

- Unit tests for utility functions
- Component tests with React Testing Library
- End-to-end tests with Cypress
- Visual regression tests with Storybook

### Pipeline Testing

- Test with sample datasets
- Validate outputs against expected results
- Measure performance metrics

## Documentation

All code should be properly documented:

- **Backend**: Docstrings for all functions and classes
- **Frontend**: JSDoc comments for components and functions
- **API**: OpenAPI/Swagger documentation
- **Pipelines**: README files with usage instructions
- **Infrastructure**: Comments for resource configurations

## Performance Considerations

### Backend Performance

- Use async operations for database and external services
- Implement caching for frequently accessed data
- Optimize database queries
- Use connection pooling
- Monitor request/response times

### Frontend Performance

- Implement code splitting
- Optimize bundle size
- Use lazy loading for components
- Implement proper state management
- Optimize rendering performance

### Database Performance

- Use appropriate indexes
- Optimize query patterns
- Use database-specific optimizations for PostgreSQL
- Monitor query performance
- Implement connection pooling

## Security Practices

### Authentication and Authorization

- Use JWT tokens for authentication
- Implement proper authorization checks
- Keep tokens short-lived
- Use HTTPS in all environments
- Implement CSRF protection

### Data Protection

- Never log sensitive information
- Use environment variables for secrets
- Validate all user inputs
- Implement proper error handling
- Follow the principle of least privilege

### API Security

- Rate limit API requests
- Validate request payloads
- Return appropriate HTTP status codes
- Implement proper CORS configuration
- Use security headers

## Monitoring and Logging

### Logging Strategy

- Use structured logging
- Log appropriate context with each entry
- Separate logs by severity level
- Don't log sensitive information
- Implement contextual logging

### Monitoring

- Monitor application health
- Track performance metrics
- Set up alerts for critical issues
- Monitor resource usage
- Implement distributed tracing

## Deployment

See the [Deployment Guide](deployment.md) for detailed instructions on deploying the platform to production environments.

## Troubleshooting

### Common Issues

- **Database connection errors**: Check connection parameters and network access
- **AWS permission issues**: Verify IAM roles and policies
- **Pipeline execution failures**: Check Nextflow logs and AWS Batch status
- **API errors**: Check server logs and request payloads
- **Frontend build issues**: Check dependencies and build logs

### Getting Help

If you encounter issues not covered in this guide:

1. Check the project documentation
2. Search existing GitHub issues
3. Ask questions in the team communication channels
4. Create a new GitHub issue with detailed information
