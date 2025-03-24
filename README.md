# Nextflow Pipeline Platform

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.11-009688.svg)](https://fastapi.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A scalable platform for executing Nextflow pipelines on AWS with a FastAPI backend and React frontend.

<div align="center">
  <img src="docs/assets/architecture_simple.md" alt="Architecture Diagram" width="650">
</div>

## 1. Overview

> ⏱️ **Time to read**: 5 minutes

The Nextflow Pipeline Platform provides a web-based interface for managing, executing, and monitoring bioinformatics pipelines built with the Nextflow framework. It leverages AWS infrastructure for scalable, cloud-based execution of compute-intensive pipelines.

**Key Features:**
- 🔐 User authentication with JWT
- 🧬 Pipeline management and versioning
- 🚀 Job submission with customizable parameters
- 📊 Real-time status monitoring
- ☁️ AWS infrastructure integration
- 🔄 RESTful API for programmatic access

For a detailed architecture overview, see [Architecture Documentation](./docs/architecture_diagram.md).

## 2. Quick Start Guide

### Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL 14+
- AWS Account with appropriate permissions
- Docker (for local development)

### One-line Setup (Development)

```bash
# Clone and set up the complete development environment
git clone https://github.com/yourusername/nextflow-pipeline-platform.git && cd nextflow-pipeline-platform && ./scripts/setup_dev.sh
```

### Step-by-step Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/nextflow-pipeline-platform.git
   cd nextflow-pipeline-platform
   ```

2. **Backend setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   cp .env.example .env      # Edit with your configuration
   alembic upgrade head      # Initialize database
   uvicorn app.main:app --reload
   ```
   
   Expected output:
   ```
   INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
   INFO:     Started reloader process [28720]
   INFO:     Started server process [28722]
   INFO:     Waiting for application startup.
   INFO:     Application startup complete.
   ```

3. **Frontend setup**
   ```bash
   cd frontend
   npm install
   cp .env.example .env      # Edit with your configuration
   npm start
   ```
   
   Expected output:
   ```
   Compiled successfully!
   
   You can now view nextflow-pipeline-platform in the browser.
   
   Local:            http://localhost:3000
   On Your Network:  http://192.168.1.5:3000
   ```

For more detailed setup instructions, see the [Development Guide](./docs/development.md).

## 3. Documentation

See the following documentation for more details:

- [Getting Started Guide](./docs/getting_started.md) - A step-by-step tutorial for new users
- [Developer Guide](./docs/developer_guide.md) - Architecture details and development guidelines
- [Workflow Diagrams](./docs/workflow_diagrams.md) - Visual representations of key platform processes
- [Installation Guide](./docs/installation_guide.md) - Multi-environment setup instructions
- [Frequently Asked Questions](./docs/faq.md) - Common questions and troubleshooting tips

## 4. Project Structure

```
/
├── backend/                # FastAPI Python backend
│   ├── app/                # API code
│   ├── db/                 # Database models
│   └── tests/              # Backend tests
├── frontend/               # React frontend
├── pipeline/               # Nextflow pipeline definitions
├── infra/                  # Terraform infrastructure code
└── docs/                   # Documentation
```

## 5. Development Workflow

### Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

See the [Development Guide](./docs/development.md) for coding standards and best practices.

## 6. Deployment

For production deployment on AWS:

1. Configure AWS credentials
2. Customize Terraform variables
3. Apply Terraform configuration
4. Deploy application components

Detailed instructions available in the [Deployment Guide](./docs/deployment.md).

## 7. License

This project is licensed under the MIT License - see the LICENSE file for details.

## 8. Project Status

This project is actively maintained. For roadmap information, see [Roadmap](./docs/roadmap.md).

## 9. FAQ

See the [Frequently Asked Questions](./docs/faq.md) document for common questions and troubleshooting tips.
