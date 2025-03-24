# Nextflow Pipeline Platform: Workflow Diagrams

> 🗓️ **Last updated**: March 24, 2025

<div align="center">
<h2>📊 Visual Workflow Documentation</h2>
</div>

This document provides visual diagrams of the key workflows in the Nextflow Pipeline Platform, designed to help users and developers understand the system processes.

## 📑 Table of Contents

- [🚀 Pipeline Submission and Execution Workflow](#-pipeline-submission-and-execution-workflow)
- [🔄 Data Processing Workflow](#-data-processing-workflow)
- [🔐 User Authentication and Authorization Flow](#-user-authentication-and-authorization-flow)
- [⚙️ Pipeline Development Lifecycle](#️-pipeline-development-lifecycle)
- [🛠️ Error Handling and Recovery Processes](#️-error-handling-and-recovery-processes)

---

## 🚀 Pipeline Submission and Execution Workflow

<div align="center">
<h3>From Submission to Results: The Complete Journey</h3>
</div>

The diagram below illustrates the flow of submitting and executing a pipeline:

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│             │     │             │     │             │     │             │     │             │
│    User     │     │   Frontend  │     │  Backend    │     │  Nextflow   │     │    AWS      │
│             │     │             │     │             │     │             │     │             │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │                   │                   │
       │                   │                   │                   │                   │
       │ 1. Select pipeline│                   │                   │                   │
       │ and parameters    │                   │                   │                   │
       │ ────────────────► │                   │                   │                   │
       │                   │                   │                   │                   │
       │                   │ 2. Submit job     │                   │                   │
       │                   │ ────────────────► │                   │                   │
       │                   │                   │                   │                   │
       │                   │                   │ 3. Validate input │                   │
       │                   │                   │ ───────┐          │                   │
       │                   │                   │        │          │                   │
       │                   │                   │ ◄───────┘          │                   │
       │                   │                   │                   │                   │
       │                   │                   │ 4. Create job     │                   │
       │                   │                   │ record & generate │                   │
       │                   │                   │ job ID            │                   │
       │                   │                   │ ───────┐          │                   │
       │                   │                   │        │          │                   │
       │                   │                   │ ◄───────┘          │                   │
       │                   │                   │                   │                   │
       │                   │ 5. Return job ID  │                   │                   │
       │                   │ ◄───────────────── │                   │                   │
       │                   │                   │                   │                   │
       │ 6. Show job ID and│                   │                   │                   │
       │ status indicator  │                   │                   │                   │
       │ ◄───────────────── │                   │                   │                   │
       │                   │                   │                   │                   │
       │                   │                   │ 7. Execute        │                   │
       │                   │                   │ Nextflow pipeline │                   │
       │                   │                   │ ────────────────► │                   │
       │                   │                   │                   │                   │
       │                   │                   │                   │ 8. Submit to AWS  │
       │                   │                   │                   │ Batch             │
       │                   │                   │                   │ ────────────────► │
       │                   │                   │                   │                   │
       │                   │                   │                   │                   │
       │                   │                   │                   │                   │ 9. Process job
       │                   │                   │                   │                   │ ───────┐
       │                   │                   │                   │                   │        │
       │                   │                   │                   │                   │ ◄───────┘
       │                   │                   │                   │                   │
       │                   │                   │                   │ 10. Monitor job   │
       │                   │                   │                   │ status            │
       │                   │                   │                   │ ───────┐          │
       │                   │                   │                   │        │          │
       │                   │                   │                   │ ◄───────┘          │
       │                   │                   │                   │                   │
       │                   │                   │ 11. Job status    │                   │
       │                   │                   │ updates           │                   │
       │                   │                   │ ◄───────────────── │                   │
       │                   │                   │                   │                   │
       │                   │ 12. Poll for     │                   │                   │
       │                   │ status updates   │                   │                   │
       │                   │ ────────────────► │                   │                   │
       │                   │                   │                   │                   │
       │                   │ 13. Return status │                   │                   │
       │                   │ ◄───────────────── │                   │                   │
       │                   │                   │                   │                   │
       │ 14. Display status│                   │                   │                   │
       │ updates           │                   │                   │                   │
       │ ◄───────────────── │                   │                   │                   │
       │                   │                   │                   │                   │
```

<div align="center">
<p><em>The pipeline execution process spans from user selection to execution and monitoring</em></p>
</div>

---

## 🔄 Data Processing Workflow

<div align="center">
<h3>How Data Flows Through the System</h3>
</div>

The workflow for data processing in the platform:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                             🔄 Data Processing Workflow                         │
└─────────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────┐           ┌─────────────┐           ┌─────────────┐
  │             │ 1. Upload │             │2. Transfer │             │
  │   👤 User   │──────────►│   Backend   │──────────►│ S3 Bucket   │
  │             │           │             │           │             │
  └─────────────┘           └─────────────┘           └──────┬──────┘
                                                             │
                                                             │ 3. Verify 
                                                             ▼
  ┌─────────────┐           ┌─────────────┐           ┌─────────────┐
  │             │6. Retrieve│             │ 5. Process │             │
  │   👤 User   │◄──────────│   Backend   │◄──────────│  Nextflow   │
  │             │  results  │             │  data     │  Pipeline   │
  └─────────────┘           └─────────────┘           └──────┬──────┘
                                                             │
                                                             │ 4. Execute
                                                             ▼
                                                      ┌─────────────┐
                                                      │             │
                                                      │ AWS Batch   │
                                                      │             │
                                                      └─────────────┘
```

<div align="center">
<p><em>Data flows from user input to processing and back to results delivery</em></p>
</div>

---

## 🔐 User Authentication and Authorization Flow

<div align="center">
<h3>Secure Access Control System</h3>
</div>

The authentication and authorization process:

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                   🔐 Authentication and Authorization Flow                    │
└──────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────┐         ┌─────────────┐         ┌─────────────┐
  │             │ 1. Login │             │ 2. Auth  │             │
  │  👤 User    │─────────►│   Frontend  │─────────►│   Backend   │
  │             │          │             │          │             │
  └─────────────┘         └─────────────┘         └──────┬──────┘
                                                          │
                                                          │ 3. Verify
                                                          ▼
  ┌─────────────┐         ┌─────────────┐         ┌─────────────┐
  │             │6. Access │             │5. Return │             │
  │  👤 User    │◄─────────│   Frontend  │◄─────────│   Backend   │
  │             │          │             │ JWT token│             │
  └─────────────┘         └─────────────┘         └──────┬──────┘
                                                          │
                                                          │ 4. Query
                                                          ▼
                                                   ┌─────────────┐
                                                   │             │
                                                   │  Database   │
                                                   │             │
                                                   └─────────────┘

                  ┌─────────────────────────────────────────┐
                  │         Authorization Details            │
                  ├─────────────────────────────────────────┤
                  │ 1. JWT token includes user role         │
                  │ 2. API endpoints check role permissions │
                  │ 3. Resources filtered by user access    │
                  │ 4. Some actions limited to admin roles  │
                  └─────────────────────────────────────────┘
```

<div align="center">
<p><em>The security system ensures proper authentication and permission-based access</em></p>
</div>

---

## ⚙️ Pipeline Development Lifecycle

<div align="center">
<h3>From Conception to Deployment</h3>
</div>

The lifecycle of pipeline development:

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                     ⚙️ Pipeline Development Lifecycle                         │
└──────────────────────────────────────────────────────────────────────────────┘

 ┌────────────┐     ┌────────────┐     ┌────────────┐     ┌────────────┐
 │            │     │            │     │            │     │            │
 │   Design   │────►│   Develop  │────►│    Test    │────►│   Deploy   │
 │            │     │            │     │            │     │            │
 └────────────┘     └────────────┘     └────────────┘     └────────────┘
        │                 │                  │                  │
        ▼                 ▼                  ▼                  ▼
 ┌────────────┐     ┌────────────┐     ┌────────────┐     ┌────────────┐
 │• Define     │     │• Write     │     │• Local     │     │• Register  │
 │  workflow   │     │  Nextflow  │     │  testing   │     │  in system │
 │• Identify   │     │  script    │     │• Small     │     │• Configure │
 │  inputs &   │     │• Create    │     │  dataset   │     │  parameters│
 │  outputs    │     │  container │     │  validation│     │• Document  │
 │• Plan       │     │  images    │     │• Edge case │     │  usage     │
 │  resources  │     │• Define    │     │  testing   │     │            │
 └────────────┘     └────────────┘     └────────────┘     └────────────┘

                                                                │
                                                                ▼
 ┌────────────┐     ┌────────────┐     ┌────────────┐     ┌────────────┐
 │            │     │            │     │            │     │            │
 │  Monitor   │◄────│    Run     │◄────│   Share    │◄────│  Version   │
 │            │     │            │     │            │     │            │
 └────────────┘     └────────────┘     └────────────┘     └────────────┘
        │                 │                  │                  │
        ▼                 ▼                  ▼                  ▼
 ┌────────────┐     ┌────────────┐     ┌────────────┐     ┌────────────┐
 │• Track     │     │• Execute   │     │• Publish   │     │• Tag       │
 │  performance│     │  pipeline  │     │  pipeline  │     │  releases  │
 │• Resource   │     │• Process   │     │• Document  │     │• Track     │
 │  usage      │     │  real data │     │  features  │     │  changes   │
 │• Log        │     │• Scale as  │     │• Add to    │     │• Maintain  │
 │  analysis   │     │  needed    │     │  catalog   │     │  backcompat│
 └────────────┘     └────────────┘     └────────────┘     └────────────┘
```

<div align="center">
<p><em>The complete lifecycle shows how pipelines evolve from concept to production</em></p>
</div>

---

## 🛠️ Error Handling and Recovery Processes

<div align="center">
<h3>Robust Error Management</h3>
</div>

The error handling and recovery flow:

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                    🛠️ Error Handling and Recovery Process                     │
└──────────────────────────────────────────────────────────────────────────────┘

                          ┌─────────────────┐
                          │                 │
                          │ Pipeline Process│
                          │                 │
                          └────────┬────────┘
                                   │
                                   │
               ┌──────────────────┴───────────────────┐
               │                                      │
               ▼                                      ▼
      ┌─────────────────┐                    ┌─────────────────┐
      │                 │                    │                 │
      │   Normal        │                    │    Error        │
      │   Execution     │                    │    Detected     │
      │                 │                    │                 │
      └─────────────────┘                    └────────┬────────┘
                                                      │
                                                      │
                                      ┌───────────────┴───────────────┐
                                      │                               │
                                      ▼                               ▼
                              ┌─────────────────┐           ┌─────────────────┐
                              │                 │           │                 │
                              │   Recoverable   │           │  Non-recoverable│
                              │   Error         │           │  Error          │
                              │                 │           │                 │
                              └────────┬────────┘           └────────┬────────┘
                                       │                             │
                                       │                             │
                                       ▼                             ▼
                              ┌─────────────────┐           ┌─────────────────┐
                              │                 │           │                 │
                              │ Retry Mechanism │           │ Terminate Job   │
                              │                 │           │                 │
                              └────────┬────────┘           └────────┬────────┘
                                       │                             │
                                       │                             │
                         ┌─────────────┴───────────┐                │
                         │                         │                │
                         ▼                         ▼                │
               ┌─────────────────┐       ┌─────────────────┐       │
               │                 │       │                 │       │
               │ Retry Success   │       │ Retry Failed    │       │
               │                 │       │                 │       │
               └────────┬────────┘       └────────┬────────┘       │
                        │                         │                │
                        │                         │                │
                        ▼                         ▼                ▼
               ┌─────────────────┐       ┌─────────────────┐      │
               │                 │       │                 │      │
               │ Resume Pipeline │       │ Fallback        │      │
               │                 │       │ Procedure       │      │
               └────────┬────────┘       └────────┬────────┘      │
                        │                         │                │
                        │                         │                │
                        ▼                         │                │
               ┌─────────────────┐                │                │
               │                 │                │                │
               │ Complete Job    │◄───────────────┘                │
               │                 │◄───────────────────────────────┘
               └─────────────────┘

```

### 📋 Error Recovery Strategies

<div align="center">

| Error Type | Recovery Strategy |
|------------|-------------------|
| ⏱️ **Timeout** | • Retry with increased timeout<br>• Allocate more resources |
| 💾 **Resource limit** | • Retry with more memory/CPU<br>• Split task into smaller chunks |
| 📡 **Data transfer** | • Retry transfer<br>• Use alternative data source |
| 🔑 **Authentication** | • Refresh credentials<br>• Alert admin |
| 🧮 **Pipeline error** | • Resume from last checkpoint<br>• Skip failed task if possible |

</div>

<div align="center">
<p><em>The error handling system ensures robust pipeline execution even when issues occur</em></p>
</div>

---

<div align="center">
<h3>📚 Related Documentation</h3>

[Developer Guide](developer_guide.md) • [Architecture Diagram](architecture_diagram.md) • [API Documentation](api.md) • [Getting Started Guide](getting_started.md)
</div>
