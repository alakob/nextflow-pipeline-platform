# User Guide

> ⏱️ **Time to read**: 20 minutes  
> 🗓️ **Last updated**: March 24, 2025

## Table of Contents

- [Introduction](#introduction)
- [Getting Started](#getting-started)
  - [Account Setup](#account-setup)
  - [Login & Authentication](#login--authentication)
  - [User Profile](#user-profile)
- [Using the Platform](#using-the-platform)
  - [Pipeline Management](#pipeline-management)
  - [Job Submission](#job-submission)
  - [Job Monitoring](#job-monitoring)
  - [Results Management](#results-management)
- [Advanced Features](#advanced-features)
  - [Pipeline Customization](#pipeline-customization)
  - [Batch Processing](#batch-processing)
  - [Notifications](#notifications)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)
- [Glossary](#glossary)

## Introduction

The Nextflow Pipeline Platform allows you to run bioinformatics pipelines on AWS infrastructure through a simple web interface. This guide will walk you through the platform's functionality from account setup to advanced features.

> 💡 **NOTE:** The platform handles the complexity of cloud infrastructure, allowing you to focus on your bioinformatics workflows.

## Getting Started

### Account Setup

<details>
<summary><strong>Registering a New Account</strong></summary>

1. Navigate to the login page and click the "Register" button
2. Enter your username and a secure password
3. Click "Register" to create your account
4. You'll be automatically logged in after successful registration

![Registration Process](https://via.placeholder.com/600x300?text=Registration+Screen+Screenshot)

</details>

### Login & Authentication

> 🔒 **Security Note:** The platform uses JWT-based authentication with tokens that expire after 30 minutes of inactivity.

1. Enter your username and password
2. Click "Login" to access the platform
3. Your session will remain active for 30 minutes after your last action

If your session expires, you'll need to log in again to continue using the platform.

### User Profile

<details>
<summary><strong>Managing Your Profile</strong></summary>

Access your profile by clicking on your username in the top-right corner of any page.

From your profile page, you can:
- Update your contact information
- Change your password
- Set notification preferences
- View your API access tokens

</details>

## Using the Platform

### Pipeline Management

#### Browsing Available Pipelines

The "Pipelines" section displays all pipelines available to you, with key information:

| Column | Description |
|--------|-------------|
| Name | Pipeline identifier |
| Description | Brief overview of pipeline function |
| Last Updated | When the pipeline was last modified |
| Runtime | Typical execution time |

> 🔍 **Tip:** Use the search bar to filter pipelines by name, description, or tags.

#### Pipeline Details

Click on any pipeline to view detailed information:

- Full description and documentation
- Required parameters with descriptions
- Example input/output formats
- Version history
- Typical resource requirements

### Job Submission

<details>
<summary><strong>Step-by-Step Job Submission Guide</strong></summary>

1. **Select a Pipeline**
   - Navigate to "Pipelines"
   - Click on your desired pipeline
   - Review requirements and parameters

2. **Configure Parameters**
   - Fill in required fields (marked with *)
   - Select appropriate compute resources
   - Specify input data location (S3 paths)
   - Set output destination

3. **Review & Submit**
   - Check your configuration
   - Estimate runtime and cost
   - Click "Submit Job"

4. **Confirmation**
   - Copy the job ID for your records
   - View job status on the Jobs dashboard

![Job Submission Workflow](https://via.placeholder.com/800x400?text=Job+Submission+Workflow)

</details>

#### Common Parameters

The following parameters are common across many pipeline types:

| Parameter | Description | Example | Required |
|-----------|-------------|---------|----------|
| `reads` | Input FASTQ files | s3://bucket/reads/*.fastq | Yes |
| `genome` | Reference genome | s3://bucket/reference/hg38.fa | Yes |
| `max_memory` | Maximum memory allocation | 16.GB | No (Default: 8.GB) |
| `max_cpus` | Maximum CPU cores | 4 | No (Default: 2) |
| `output_dir` | Output directory | s3://bucket/results/my-analysis | No (Default: auto-generated) |

> ⚠️ **Important:** Ensure your AWS credentials have access to both input and output S3 locations.

### Job Monitoring

The Jobs dashboard provides real-time monitoring of all your pipeline runs.

#### Job Status Indicators

| Status | Color | Description |
|--------|-------|-------------|
| 🟦 QUEUED | Blue | Job is waiting for resources |
| 🟨 PREPARING | Yellow | Setting up execution environment |
| 🟩 RUNNING | Green | Job is actively running |
| ✅ COMPLETED | Green check | Job completed successfully |
| ❌ FAILED | Red | Job failed during execution |
| ⏹️ CANCELLED | Gray | Job was manually cancelled |

#### Job Details View

Click on any job to access the detailed view with four tabs:

1. **Overview Tab**
   - Job metadata
   - Status information
   - Execution timeline
   - Resource utilization graphs

2. **Parameters Tab**
   - All parameters used for this job
   - Input data location
   - Output data location

3. **Logs Tab**
   - Execution logs with search functionality
   - Error messages (if any)
   - Process-specific outputs

4. **Results Tab**
   - Links to output files in S3
   - Summary metrics (if available)
   - Visualization of results (if available)

### Results Management

Once a job completes, you can manage the results:

- **View Results**: Browse output files directly in the web interface
- **Download Results**: Get individual files or the complete output directory
- **Share Results**: Generate time-limited shareable links
- **Archive Results**: Move to long-term storage with reduced access costs
- **Delete Results**: Remove unnecessary output files to reduce storage costs

> 💡 **Tip:** Set up automatic notifications to be alerted when jobs complete.

## Advanced Features

### Pipeline Customization

<details>
<summary><strong>Using Advanced Parameters</strong></summary>

1. On the job submission page, toggle "Show Advanced Options"
2. Configure additional parameters:
   - Tool-specific settings
   - Performance tuning options
   - Alternative algorithms
   - Debug/verbose mode settings

For maximum flexibility, you can also upload custom Nextflow configuration files:

```bash
# Example custom config snippet
process {
  withName: 'FASTQC' {
    container = 'custom/fastqc:latest'
    memory = 4.GB
  }
}
```

</details>

### Batch Processing

For processing multiple samples with similar parameters:

1. Create a CSV sample sheet with per-sample parameters
2. Upload the sample sheet during job submission
3. Configure batch-wide parameters that apply to all samples
4. Submit as a single batch job

Example sample sheet format:
```csv
sample_id,reads,condition
sample1,s3://bucket/sample1.fastq,control
sample2,s3://bucket/sample2.fastq,treated
sample3,s3://bucket/sample3.fastq,treated
```

### Notifications

<details>
<summary><strong>Setting Up Email Notifications</strong></summary>

1. Navigate to your user profile
2. Select the "Notifications" tab
3. Enter your email address
4. Choose which events trigger notifications:
   - Job started
   - Job completed
   - Job failed
   - Job cancelled
5. Set notification frequency (immediate, hourly digest, daily digest)

For programmatic notifications, you can also set up webhooks in the API settings section.

</details>

## Troubleshooting

### Common Issues and Solutions

<details>
<summary><strong>Job Fails Immediately After Submission</strong></summary>

**Possible causes:**
- Invalid input file paths
- Insufficient AWS permissions
- Missing required parameters

**Solutions:**
1. Verify S3 paths are correct and accessible
2. Check AWS credentials and permissions
3. Review job logs for specific error messages
4. Ensure all required parameters are provided

</details>

<details>
<summary><strong>Job Runs But Produces Unexpected Results</strong></summary>

**Possible causes:**
- Incompatible input data format
- Parameter misconfiguration
- Pipeline version mismatch

**Solutions:**
1. Validate input data format against pipeline requirements
2. Review parameter documentation and adjust settings
3. Check if you're using the correct pipeline version
4. Contact support with job ID for assistance

</details>

<details>
<summary><strong>Performance Issues</strong></summary>

**Possible causes:**
- Insufficient compute resources
- Large input data files
- Network bottlenecks

**Solutions:**
1. Increase CPU/memory allocation
2. Consider splitting large datasets
3. Optimize input data (compression, filtering)
4. Choose AWS regions closer to your data

</details>

### Getting Help

If you encounter issues not covered in this guide:

1. Check detailed job logs
2. Review pipeline documentation
3. Contact support via the help desk
4. Include your job ID in all communications

## Best Practices

### Resource Management

- **Right-size your resources**: Start with recommended settings, then adjust based on performance
- **Clean up regularly**: Delete unnecessary output files to reduce storage costs
- **Archive important results**: Move completed data to archival storage for long-term retention

### Workflow Organization

- **Use consistent naming**: Adopt a clear naming convention for jobs
- **Document your runs**: Add detailed descriptions to jobs for future reference
- **Group related analyses**: Use tags to organize related jobs

### Data Management

- **Organize input data**: Structure S3 buckets logically
- **Version reference data**: Track which versions of reference genomes were used
- **Back up critical results**: Maintain copies of important outputs

## Glossary

| Term | Definition |
|------|------------|
| Pipeline | A Nextflow workflow that processes biological data |
| Job | A single execution of a pipeline with specific parameters |
| Nextflow | A workflow language for computational pipelines |
| AWS Batch | AWS service for batch computing jobs |
| S3 | Simple Storage Service, AWS's object storage |
| Container | Docker/Singularity container with bioinformatics tools |
| Work Directory | Temporary storage for intermediate files |
| Output Directory | Location for final results |

---

**Need More Help?**
- [API Documentation](api.md)
- [Pipeline Development Guide](pipeline_development.md)
- [Frequently Asked Questions](faq.md)
