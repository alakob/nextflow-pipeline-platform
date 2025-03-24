# Nextflow Pipeline Platform Architecture

This document provides a comprehensive overview of the Nextflow Pipeline Platform architecture using Mermaid diagrams.

## System Architecture

```mermaid
graph TB
    subgraph "Frontend"
        UI[React UI]
        UIstate[State Management]
        UIcomponents[UI Components]
    end

    subgraph "Backend"
        API[FastAPI Application]
        Auth[Authentication]
        Router[API Routers]
        Services[Services]
        
        subgraph "Database"
            Models[SQLAlchemy Models]
            DB[(PostgreSQL)]
        end
    end

    subgraph "Pipeline Infrastructure"
        NF[Nextflow Engine]
        AWS[AWS Batch/S3]
        Containers[Docker Containers]
    end

    subgraph "Deployment Infrastructure"
        TF[Terraform]
        CI[CI/CD Pipeline]
    end

    UI --> API
    API --> Auth
    API --> Router
    Router --> Services
    Services --> Models
    Models --> DB
    Services --> NF
    NF --> AWS
    NF --> Containers
    TF --> AWS
    CI --> API
    CI --> UI
```

## Component Relationship Diagram

```mermaid
classDiagram
    class User {
        +id: UUID
        +username: String
        +hashed_password: String
        +role: String
    }
    
    class Pipeline {
        +id: UUID
        +name: String
        +description: String
        +nextflow_config: Text
    }
    
    class Job {
        +id: UUID
        +user_id: UUID
        +pipeline_id: UUID
        +status: String
        +parameters: Text
        +created_at: DateTime
        +updated_at: DateTime
        +external_id: String
        +work_dir: String
        +output_dir: String
        +started_at: DateTime
        +completed_at: DateTime
        +description: String
    }
    
    class AuthModule {
        +verify_password()
        +get_password_hash()
        +create_access_token()
        +get_current_user()
        +get_current_active_user()
    }
    
    class PipelineRouter {
        +get_pipelines()
        +get_pipeline()
        +create_pipeline_job()
        +get_pipeline_job()
        +cancel_pipeline_job()
        +list_pipeline_jobs()
    }
    
    class PipelineService {
        +run_pipeline()
        +get_pipeline_status()
        +cancel_pipeline()
    }

    User "1" --> "*" Job : creates
    Pipeline "1" --> "*" Job : executes
    PipelineRouter --> PipelineService : uses
    PipelineRouter --> AuthModule : authenticates
    PipelineService --> Job : manages
```

## API Flow Diagram

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant Auth
    participant Router
    participant Service
    participant Database
    participant NextflowEngine
    
    Client->>API: Register User
    API->>Auth: Hash Password
    Auth-->>API: Password Hashed
    API->>Database: Store User
    Database-->>API: User Created
    API-->>Client: User Created Response
    
    Client->>API: Login Request
    API->>Auth: Verify Credentials
    Auth->>Database: Query User
    Database-->>Auth: User Data
    Auth-->>API: JWT Token
    API-->>Client: Access Token
    
    Client->>API: Request Pipeline List
    API->>Auth: Validate Token
    Auth-->>API: User Authenticated
    API->>Router: Get Pipelines
    Router->>Database: Query Pipelines
    Database-->>Router: Pipeline List
    Router-->>API: Pipeline Data
    API-->>Client: Pipeline List Response
    
    Client->>API: Submit Pipeline Job
    API->>Auth: Validate Token
    Auth-->>API: User Authenticated
    API->>Router: Create Job
    Router->>Service: Run Pipeline
    Service->>Database: Create Job Record
    Database-->>Service: Job Created
    Service->>NextflowEngine: Execute Pipeline
    NextflowEngine-->>Service: Execution Started
    Service-->>Router: Job Status
    Router-->>API: Job Created
    API-->>Client: Job Submission Response
    
    Client->>API: Get Job Status
    API->>Auth: Validate Token
    Auth-->>API: User Authenticated
    API->>Router: Get Job
    Router->>Database: Query Job
    Database-->>Router: Job Data
    Router->>Service: Check Pipeline Status
    Service->>NextflowEngine: Get Status
    NextflowEngine-->>Service: Current Status
    Service-->>Router: Updated Status
    Router-->>API: Job Status
    API-->>Client: Job Status Response
```

## Database Schema

```mermaid
erDiagram
    USER {
        uuid id PK
        string username
        string hashed_password
        string role
    }
    
    PIPELINE {
        uuid id PK
        string name
        string description
        text nextflow_config
    }
    
    JOB {
        uuid id PK
        uuid user_id FK
        uuid pipeline_id FK
        string status
        text parameters
        datetime created_at
        datetime updated_at
        string external_id
        string work_dir
        string output_dir
        datetime started_at
        datetime completed_at
        string description
    }
    
    USER ||--o{ JOB : creates
    PIPELINE ||--o{ JOB : executes
```

## Authentication Flow

```mermaid
sequenceDiagram
    participant Client
    participant FastAPI
    participant Auth
    participant Database
    
    Client->>FastAPI: POST /login
    FastAPI->>Auth: Verify credentials
    Auth->>Database: Query user by username
    Database-->>Auth: Return user data
    Auth->>Auth: Verify password
    Auth->>Auth: Generate JWT token
    Auth-->>FastAPI: Return token
    FastAPI-->>Client: Access token + token type
    
    Client->>FastAPI: API Request with Bearer token
    FastAPI->>Auth: Validate token
    Auth->>Auth: Decode JWT
    Auth->>Database: Get user by ID
    Database-->>Auth: User data
    Auth-->>FastAPI: Current user
    FastAPI-->>Client: API Response
```

## Pipeline Execution Flow

```mermaid
flowchart TD
    A[User submits job] --> B{Validate Input}
    B -->|Valid| C[Create job record in DB]
    B -->|Invalid| D[Return validation error]
    C --> E[Generate job ID and paths]
    E --> F[Build Nextflow command]
    F --> G[Execute Nextflow process]
    G --> H[Update job status to RUNNING]
    H --> I[Monitor execution]
    I --> J{Job completed?}
    J -->|No| I
    J -->|Yes| K[Update final status]
    K --> L[Store results location]
    
    M[User requests job status] --> N[Fetch job from DB]
    N --> O[Check external job status]
    O --> P[Return current status]
    
    Q[User cancels job] --> R[Validate job ownership]
    R --> S[Send cancel signal to Nextflow]
    S --> T[Update job status to CANCELLED]
```
