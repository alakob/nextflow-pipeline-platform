# Pipeline Development Guide

This guide provides detailed information for developing and integrating Nextflow pipelines with the Nextflow Pipeline Platform.

## Overview

The platform is designed to run bioinformatics workflows written in Nextflow, a domain-specific language for writing data-intensive computational pipelines. Pipelines are executed on AWS infrastructure, providing scalable and cost-effective computing resources.

## Pipeline Structure

### Directory Structure

Pipelines are stored in the `pipeline` directory with the following structure:

```
pipeline/
├── nextflow           # Nextflow executable
├── test.nf            # Example pipeline
├── modules/           # Reusable pipeline components
│   ├── fastqc.nf      # FastQC module
│   └── trim.nf        # Trimming module
├── conf/              # Configuration files
│   ├── aws.config     # AWS-specific configurations
│   └── base.config    # Base configuration for all environments
└── templates/         # Template scripts and files
```

### Pipeline Components

A typical Nextflow pipeline consists of:

1. **Main Workflow File**: Defines the overall workflow, including inputs, outputs, and process execution order
2. **Processes**: Individual computational steps (e.g., quality control, alignment, variant calling)
3. **Configuration**: Parameters and execution environment settings

## Developing a New Pipeline

### Creating a Basic Pipeline

1. Create a new `.nf` file in the `pipeline` directory:

```groovy
#!/usr/bin/env nextflow

// Pipeline parameters
params.reads = "s3://example-bucket/reads/*.fastq"
params.genome = "s3://example-bucket/reference/genome.fa"
params.outdir = "s3://example-bucket/results"

// Log parameters
log.info """\
         N E X T F L O W  P I P E L I N E
         =============================
         reads        : ${params.reads}
         genome       : ${params.genome}
         outdir       : ${params.outdir}
         """
         .stripIndent()

// Include modules
include { FASTQC } from './modules/fastqc'
include { BWA_ALIGN } from './modules/align'
include { VARIANT_CALL } from './modules/variants'

// Main workflow
workflow {
    // Channel for input reads
    reads_ch = Channel
        .fromPath(params.reads)
        .map { file -> tuple(file.simpleName, file) }
    
    // Run FastQC on raw reads
    FASTQC(reads_ch)
    
    // Align reads to reference genome
    BWA_ALIGN(reads_ch, params.genome)
    
    // Call variants
    VARIANT_CALL(BWA_ALIGN.out, params.genome)
}
```

### Creating Modules

For reusable components, create module files in the `modules` directory:

```groovy
// modules/fastqc.nf
process FASTQC {
    tag "${sample_id}"
    publishDir "${params.outdir}/fastqc", mode: 'copy'
    
    input:
    tuple val(sample_id), path(reads)
    
    output:
    path "${sample_id}_fastqc.html"
    path "${sample_id}_fastqc.zip"
    
    script:
    """
    fastqc -q $reads
    """
}
```

### Configuration

Create configuration files in the `conf` directory:

```groovy
// conf/aws.config
process {
    executor = 'awsbatch'
    queue = 'nextflow-pipeline-queue'
    container = 'quay.io/biocontainers/fastqc:0.11.9--0'
    
    withName: 'FASTQC' {
        container = 'quay.io/biocontainers/fastqc:0.11.9--0'
    }
    
    withName: 'BWA_ALIGN' {
        container = 'quay.io/biocontainers/bwa:0.7.17--h5bf99c6_7'
    }
}

aws {
    region = 'eu-north-1'
    batch {
        cliPath = '/usr/local/bin/aws'
    }
}
```

## Integrating with the Platform

### Registering a Pipeline

To make a pipeline available in the platform:

1. Add an entry in the database through the admin interface or API
2. Provide the pipeline name, description, and Nextflow configuration
3. Specify default parameters and input requirements

### Parameter Schema Definition

Define the expected parameters for your pipeline using a JSON schema:

```json
{
  "title": "Pipeline Parameters",
  "type": "object",
  "properties": {
    "reads": {
      "type": "string",
      "description": "Input reads (S3 path to FASTQ files)"
    },
    "genome": {
      "type": "string",
      "description": "Reference genome (S3 path to FASTA file)"
    },
    "max_memory": {
      "type": "string",
      "default": "16.GB",
      "description": "Maximum memory to use"
    },
    "max_cpus": {
      "type": "integer",
      "default": 4,
      "description": "Maximum CPUs to use"
    }
  },
  "required": ["reads", "genome"]
}
```

## Test and Debug Pipelines

### Local Testing

Test pipelines locally before deploying to AWS:

```bash
cd pipeline
./nextflow run test.nf -profile docker
```

### AWS Testing

Test on AWS with a small dataset:

```bash
cd pipeline
./nextflow run test.nf -profile aws -work-dir s3://your-bucket/work
```

### Debugging

- Use `nextflow log` to inspect execution history
- Check the `.nextflow.log` file for detailed logs
- Add `println` statements for debugging specific values
- Use the `-resume` flag to restart from the last successful process

## Best Practices

### Pipeline Development

1. **Modularize** your code into reusable processes
2. **Containerize** all tools using Docker
3. **Parameterize** everything for flexibility
4. **Document** your code with comments
5. **Version** your pipelines with Git
6. **Test** with small datasets first

### Performance Optimization

1. **Use AWS Batch** for cost-effective computing
2. **Enable process-specific resources** based on actual requirements
3. **Implement conditional execution** to skip unnecessary steps
4. **Use published outputs** to avoid recomputation
5. **Optimize container images** for faster startup

### Data Management

1. **Use S3 for input and output** data
2. **Structure output directories** logically
3. **Compress outputs** when possible
4. **Include QC metrics** in the results
5. **Publish important intermediate files** for debugging

## Advanced Features

### Workflow Reporting

Use Nextflow's built-in reporting features:

```groovy
workflow.onComplete {
    log.info "Pipeline completed at: $workflow.complete"
    log.info "Execution status: ${ workflow.success ? 'OK' : 'failed' }"
    log.info "Execution duration: $workflow.duration"
}
```

### Error Handling

Implement robust error handling:

```groovy
process ERROR_PRONE {
    errorStrategy 'retry'
    maxRetries 3
    
    script:
    """
    # Your commands here
    """
}
```

### Resource Scaling

Dynamically allocate resources based on input size:

```groovy
process MEMORY_INTENSIVE {
    memory { 2.GB * task.attempt }
    time { 1.hour * task.attempt }
    errorStrategy 'retry'
    maxRetries 3
    
    script:
    """
    # Your commands here
    """
}
```

## Resources

- [Nextflow Documentation](https://www.nextflow.io/docs/latest/index.html)
- [nf-core Guidelines](https://nf-co.re/docs/guidelines/pipelines/overview)
- [AWS Batch Documentation](https://docs.aws.amazon.com/batch/latest/userguide/what-is-batch.html)
- [Biocontainers Registry](https://biocontainers.pro/)
