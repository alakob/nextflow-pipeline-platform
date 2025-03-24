# Nextflow Pipeline Platform Architecture

> **Last updated**: March 24, 2025

## Table of Contents

- [System Architecture](#system-architecture)
- [Component Interaction](#component-interaction)
- [Key Workflows](#key-workflows)
  - [User Authentication Flow](#user-authentication-flow)
  - [Pipeline Execution Flow](#pipeline-execution-flow)
  - [Data Management Flow](#data-management-flow)
- [Infrastructure Architecture](#infrastructure-architecture)
- [Security Architecture](#security-architecture)

## System Architecture

The Nextflow Pipeline Platform is built on a modern, scalable architecture consisting of several key components. This diagram illustrates the high-level system architecture:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        Nextflow Pipeline Platform                        │
└─────────────────────────────────────────────────────────────────────────┘
                                     │
                 ┌─────────────────────────────────────────┐
                 ▼                   │                     ▼
    ┌─────────────────────┐ ┌─────────────────┐ ┌──────────────────────┐
    │                     │ │                 │ │                      │
    │    Frontend App     │ │    Backend API  │ │  Admin Dashboard     │
    │    (React)          │ │    (FastAPI)    │ │  (React)             │
    │                     │ │                 │ │                      │
    └─────────────────────┘ └─────────────────┘ └──────────────────────┘
             │                       │                     │
             └───────────┬───────────┴─────────┬──────────┘
                         │                     │
                         ▼                     ▼
          ┌──────────────────────┐   ┌──────────────────────┐
          │                      │   │                      │
          │  User Authentication │   │  Pipeline Execution  │
          │  Service             │   │  Service             │
          │                      │   │                      │
          └──────────────────────┘   └──────────────────────┘
                     │                          │
                     │                          │
          ┌──────────────────────┐   ┌──────────────────────┐
          │                      │   │                      │
          │  User Database       │   │  Workflow Engine     │
          │  (PostgreSQL)        │   │  (Nextflow)          │
          │                      │   │                      │
          └──────────────────────┘   └──────────────────────┘
                                              │
                      ┌────────────────────────────────────────┐
                      ▼                      │                 ▼
          ┌──────────────────────┐ ┌──────────────────────┐ ┌──────────────────────┐
          │                      │ │                      │ │                      │
          │  Compute Resources   │ │  Storage             │ │  Monitoring          │
          │  (AWS Batch)         │ │  (S3)                │ │  (CloudWatch)        │
          │                      │ │                      │ │                      │
          └──────────────────────┘ └──────────────────────┘ └──────────────────────┘
```

## Component Interaction

This diagram shows how the different components interact with each other:

```
                           ┌─────────────────┐
                           │                 │
                           │     User        │
                           │                 │
                           └───────┬─────────┘
                                   │
                                   ▼
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│                 │      │                 │      │                 │
│     Frontend    │◄────►│     Backend     │◄────►│    Database     │
│                 │      │                 │      │                 │
└─────────────────┘      └────────┬────────┘      └─────────────────┘
                                  │
                                  │
                         ┌────────┴────────┐
                         │                 │
                         │    Nextflow     │
                         │    Engine       │
                         │                 │
                         └────────┬────────┘
                                  │
                   ┌──────────────┼──────────────┐
                   │              │              │
                   ▼              ▼              ▼
          ┌────────────┐  ┌────────────┐  ┌────────────┐
          │            │  │            │  │            │
          │ AWS Batch  │  │    S3      │  │    ECR     │
          │            │  │            │  │            │
          └────────────┘  └────────────┘  └────────────┘
```

## Key Workflows

### User Authentication Flow

This diagram illustrates the user authentication process:

```
┌─────────┐          ┌─────────┐          ┌─────────┐          ┌─────────┐
│         │          │         │          │         │          │         │
│  User   │          │Frontend │          │ Backend │          │Database │
│         │          │         │          │         │          │         │
└────┬────┘          └────┬────┘          └────┬────┘          └────┬────┘
     │                     │                    │                    │
     │  1. Enter creds     │                    │                    │
     │ ─────────────────► │                    │                    │
     │                     │                    │                    │
     │                     │  2. Auth request   │                    │
     │                     │ ──────────────────►│                    │
     │                     │                    │                    │
     │                     │                    │  3. Verify user    │
     │                     │                    │ ──────────────────►│
     │                     │                    │                    │
     │                     │                    │  4. User verified  │
     │                     │                    │ ◄──────────────────│
     │                     │                    │                    │
     │                     │                    │  5. Generate JWT   │
     │                     │                    │ ─────┐             │
     │                     │                    │      │             │
     │                     │                    │ ◄─────┘             │
     │                     │  6. Return token   │                    │
     │                     │ ◄──────────────────│                    │
     │                     │                    │                    │
     │  7. Show dashboard  │                    │                    │
     │ ◄─────────────────  │                    │                    │
     │                     │                    │                    │
```

### Pipeline Execution Flow

This diagram shows the flow of a pipeline execution:

```
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│         │     │         │     │         │     │         │     │         │     │         │
│  User   │     │Frontend │     │ Backend │     │Database │     │Nextflow │     │   AWS   │
│         │     │         │     │         │     │         │     │         │     │         │
└────┬────┘     └────┬────┘     └────┬────┘     └────┬────┘     └────┬────┘     └────┬────┘
     │                │               │               │               │               │
     │ 1. Submit job  │               │               │               │               │
     │ ──────────────►│               │               │               │               │
     │                │               │               │               │               │
     │                │ 2. API request│               │               │               │
     │                │ ──────────────►               │               │               │
     │                │               │               │               │               │
     │                │               │ 3. Create job │               │               │
     │                │               │ ──────────────►               │               │
     │                │               │               │               │               │
     │                │               │ 4. Job created│               │               │
     │                │               │ ◄──────────────               │               │
     │                │               │               │               │               │
     │                │ 5. Job ID     │               │               │               │
     │                │ ◄──────────────               │               │               │
     │                │               │               │               │               │
     │ 6. Show job ID │               │               │               │               │
     │ ◄──────────────│               │               │               │               │
     │                │               │ 7. Start pipeline             │               │
     │                │               │ ────────────────────────────► │               │
     │                │               │               │               │               │
     │                │               │               │               │ 8. Submit to AWS
     │                │               │               │               │ ──────────────►
     │                │               │               │               │               │
     │                │               │               │               │ 9. Execute job│
     │                │               │               │               │ ◄──────────────
     │                │               │               │               │               │
     │                │               │10. Update status              │               │
     │                │               │ ◄─────────────────────────────│               │
     │                │               │               │               │               │
     │                │               │11. Save status│               │               │
     │                │               │ ──────────────►               │               │
     │                │               │               │               │               │
     │                │12. Status update              │               │               │
     │                │ ◄──────────────               │               │               │
     │                │               │               │               │               │
     │13. Update UI   │               │               │               │               │
     │ ◄──────────────│               │               │               │               │
     │                │               │               │               │               │
```

### Data Management Flow

This diagram illustrates how data flows through the system:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                             Data Flow                                    │
└─────────────────────────────────────────────────────────────────────────┘

  ┌─────────┐              ┌─────────┐              ┌─────────┐
  │         │    Upload    │         │    Process   │         │
  │  Input  │ ───────────► │  S3     │ ───────────► │ Pipeline│
  │  Data   │              │ Storage │              │ (AWS)   │
  │         │              │         │              │         │
  └─────────┘              └─────────┘              └─────────┘
                                                        │
                                                        │ Generate
                                                        ▼
  ┌─────────┐              ┌─────────┐              ┌─────────┐
  │         │   Download   │         │    Store     │         │
  │  User   │ ◄─────────── │  Web    │ ◄─────────── │ Results │
  │         │              │ Interface│              │         │
  │         │              │         │              │         │
  └─────────┘              └─────────┘              └─────────┘
```

## Infrastructure Architecture

The platform is deployed across multiple AWS services:

```
┌───────────────────────────────────────────────────────────────────────────────┐
│                               AWS Cloud                                        │
│                                                                               │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐       │
│  │             │   │             │   │             │   │             │       │
│  │ EC2/ECS     │   │ RDS         │   │ S3          │   │ Batch       │       │
│  │ (App Servers)│   │ (Database)  │   │ (Storage)   │   │ (Compute)   │       │
│  │             │   │             │   │             │   │             │       │
│  └─────────────┘   └─────────────┘   └─────────────┘   └─────────────┘       │
│         │                 │                 │                 │               │
│         └─────────────────┴─────────────────┴─────────────────┘               │
│                                    │                                          │
│  ┌─────────────┐   ┌─────────────┐ │ ┌─────────────┐   ┌─────────────┐       │
│  │             │   │             │ │ │             │   │             │       │
│  │ CloudWatch  │   │ IAM         │ │ │ Route53     │   │ CloudFront  │       │
│  │ (Monitoring)│   │ (Security)  │ │ │ (DNS)       │   │ (CDN)       │       │
│  │             │   │             │ │ │             │   │             │       │
│  └─────────────┘   └─────────────┘ │ └─────────────┘   └─────────────┘       │
│                                    │                                          │
└────────────────────────────────────┼───────────────────────────────────────────┘
                                     │
                                     ▼
                              ┌─────────────┐
                              │             │
                              │ Users       │
                              │             │
                              └─────────────┘
```

## Security Architecture

Security is implemented at multiple levels:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         Security Architecture                            │
└─────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
  │                 │   │                 │   │                 │
  │  Application    │   │  API            │   │  Infrastructure │
  │  Security       │   │  Security       │   │  Security       │
  │                 │   │                 │   │                 │
  └─────────────────┘   └─────────────────┘   └─────────────────┘
         │                     │                     │
         ▼                     ▼                     ▼
  ┌─────────────┐       ┌─────────────┐       ┌─────────────┐
  │ • Input     │       │ • JWT Auth  │       │ • VPC       │
  │   Validation│       │ • HTTPS     │       │ • Security  │
  │ • CSRF      │       │ • Rate      │       │   Groups    │
  │   Protection│       │   Limiting  │       │ • IAM Roles │
  │ • XSS       │       │ • CORS      │       │ • Encryption│
  │   Prevention│       │ • API Keys  │       │ • Firewall  │
  └─────────────┘       └─────────────┘       └─────────────┘
```

This architectural documentation provides a clear overview of the Nextflow Pipeline Platform's structure, components, and workflows. For more detailed information on specific components, please refer to the related documentation files.

**Related Documentation**:
- [Developer Guide](developer_guide.md)
- [Deployment Guide](deployment.md)
- [API Documentation](api.md)
