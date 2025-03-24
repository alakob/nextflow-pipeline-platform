#!/usr/bin/env nextflow

/*
 * Simple test workflow to verify AWS Batch execution
 */

process HELLO {
    container 'ubuntu:20.04'
    
    output:
    stdout
    
    script:
    """
    echo "Hello from AWS Batch!"
    echo "Running on host: \$(hostname)"
    echo "AWS region: \$AWS_REGION"
    date
    """
}

workflow {
    HELLO()
    | view { it.trim() }
}
