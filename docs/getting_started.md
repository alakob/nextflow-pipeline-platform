# Getting Started with Nextflow Pipeline Platform

> ⏱️ **Time to complete**: 30 minutes  
> 🗓️ **Last updated**: March 24, 2025

This tutorial will guide you through setting up and running your first pipeline on the Nextflow Pipeline Platform using sample data.

## Prerequisites

Before you begin, ensure you have:

- An account on the Nextflow Pipeline Platform
- Basic familiarity with AWS services
- AWS credentials configured with appropriate permissions

## Table of Contents

- [Step 1: Environment Setup](#step-1-environment-setup)
- [Step 2: Data Preparation](#step-2-data-preparation)
- [Step 3: Running Your First Pipeline](#step-3-running-your-first-pipeline)
- [Step 4: Monitoring Your Job](#step-4-monitoring-your-job)
- [Step 5: Analyzing Results](#step-5-analyzing-results)
- [Next Steps](#next-steps)

## Step 1: Environment Setup

First, let's make sure your environment is properly configured.

### Setting Up AWS Credentials

If you haven't configured your AWS credentials yet:

```bash
aws configure
```

Enter your Access Key ID and Secret Access Key when prompted. Set your default region to where your data is stored.

### Verifying Setup

Let's verify that your configuration is working:

```bash
# Check AWS credentials
aws sts get-caller-identity

# Should return your account ID, user ID, and ARN
```

## Step 2: Data Preparation

For this tutorial, we'll use a sample RNA-seq dataset that is already accessible in a public bucket.

### Sample Dataset

Our sample dataset consists of:
- Paired-end RNA-seq reads from a human cell line
- Human reference genome (hg38)
- Reference annotation (GTF file)

### Creating a Data Directory

Create a working directory for the analysis:

```bash
# Create an S3 bucket for your results (if you don't have one)
aws s3 mb s3://your-nextflow-results-bucket

# Verify bucket creation
aws s3 ls
```

> ⚠️ **Note**: Replace `your-nextflow-results-bucket` with your actual bucket name.

## Step 3: Running Your First Pipeline

Now we'll run a simple RNA-seq analysis pipeline using the sample data.

### Login to the Platform

1. Navigate to the Nextflow Pipeline Platform in your browser
2. Log in with your credentials
3. You'll be directed to the dashboard

### Selecting a Pipeline

1. Click on the "Pipelines" tab in the navigation bar
2. Find the "RNA-Seq Basic Analysis" pipeline
3. Click on it to view details

![Pipeline Selection](https://via.placeholder.com/800x400?text=Pipeline+Selection+Screenshot)

### Configuring the Pipeline

Fill in the pipeline parameters:

1. **Basic Parameters**:
   - **Reads**: `s3://nextflow-demo-data/rnaseq/sample1_{1,2}.fastq.gz`
   - **Reference Genome**: `s3://nextflow-demo-data/references/hg38.fa`
   - **Annotation**: `s3://nextflow-demo-data/references/hg38.gtf`
   - **Output Directory**: `s3://your-nextflow-results-bucket/rnaseq-demo/`

2. **Resource Parameters**:
   - **Max Memory**: `16.GB`
   - **Max CPUs**: `4`

3. **Advanced Parameters** (optional):
   - Leave as default for this tutorial

![Parameter Configuration](https://via.placeholder.com/800x400?text=Parameter+Configuration+Screenshot)

### Submitting the Job

1. Review all parameters
2. Click the "Submit Job" button
3. Note the Job ID that appears in the confirmation screen

## Step 4: Monitoring Your Job

After job submission, you'll be redirected to the Jobs dashboard.

### Tracking Job Progress

1. Find your job in the list (it should be at the top)
2. Observe the current status (should be "QUEUED" or "RUNNING")
3. Click on the job to view detailed information

![Job Monitoring](https://via.placeholder.com/800x400?text=Job+Monitoring+Screenshot)

### Understanding the Job Details Page

The job details page has several tabs:

1. **Overview**: Shows metadata and progress
2. **Parameters**: Lists all parameters used
3. **Logs**: Real-time logs from the pipeline execution
4. **Results**: Will show output files when complete

While your job is running, you can:
- View real-time logs to monitor progress
- Check resource utilization graphs
- See estimated completion time

## Step 5: Analyzing Results

After the job completes (approximately 15-20 minutes), you can explore the results.

### Accessing Output Files

1. Go to the "Results" tab on the job details page
2. You'll see a list of output files and directories:
   - `multiqc_report.html`: Quality control summary
   - `counts/`: Directory with gene count data
   - `bam/`: Directory with alignment files
   - `fastqc/`: Directory with read quality reports

![Results Browser](https://via.placeholder.com/800x400?text=Results+Browser+Screenshot)

### Downloading and Visualizing Results

1. Click on `multiqc_report.html` to view it in the browser
2. Use the download buttons to get files for local analysis
3. For large files like BAM files, you can directly access them in S3:

```bash
# List results
aws s3 ls s3://your-nextflow-results-bucket/rnaseq-demo/

# Download MultiQC report
aws s3 cp s3://your-nextflow-results-bucket/rnaseq-demo/multiqc_report.html ./
```

### Interpreting the Results

The RNA-seq results include:

1. **Quality Control**:
   - Read quality metrics
   - Alignment statistics
   - Sample correlation

2. **Gene Expression**:
   - Raw counts matrix
   - Normalized expression values

3. **Alignment Files**:
   - BAM files for visualization in IGV or other browsers

## Next Steps

Congratulations! You've successfully run your first pipeline on the Nextflow Pipeline Platform. Here are some next steps to explore:

1. **Customize the Pipeline**:
   - Try changing parameters to see their effect
   - Use your own data for analysis

2. **Pipeline Variants**:
   - Try the "RNA-Seq Advanced Analysis" pipeline which includes differential expression analysis
   - Explore other pipeline types (ChIP-seq, Variant Calling, etc.)

3. **Automation**:
   - Learn to use the API for programmatic job submission
   - Set up webhooks for job completion notifications

4. **Advanced Features**:
   - Explore batch processing for multiple samples
   - Try using custom Nextflow configurations

## Additional Resources

- [User Guide](user_guide.md): Complete documentation on all features
- [API Documentation](api.md): Details on programmatic access
- [Cheat Sheet](cheatsheet.md): Quick reference for common tasks
- [FAQ](faq.md): Answers to frequently asked questions

---

**Need help?** Contact our support team at support@nextflow-platform.com or use the in-app chat feature.
