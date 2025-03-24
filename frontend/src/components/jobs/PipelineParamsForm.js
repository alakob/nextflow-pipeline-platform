import React, { useState, useEffect } from 'react';

// Default parameter schemas for different pipeline types
const PIPELINE_PARAMS = {
  "RNA-Seq Analysis": {
    reads: {
      type: "text",
      label: "Input Reads Path",
      default: "s3://sample-data/reads/*.fastq.gz",
      description: "Path to input RNA-seq reads (supports wildcards)"
    },
    genome: {
      type: "text",
      label: "Reference Genome",
      default: "s3://sample-data/reference/genome.fasta",
      description: "Path to reference genome FASTA file"
    },
    annotation: {
      type: "text",
      label: "Gene Annotation",
      default: "s3://sample-data/reference/genes.gtf",
      description: "Path to gene annotation GTF file"
    },
    outdir: {
      type: "text",
      label: "Output Directory",
      default: "s3://output/rnaseq",
      description: "Path for output results"
    },
    max_memory: {
      type: "text",
      label: "Max Memory",
      default: "16.GB",
      description: "Maximum memory to allocate"
    },
    max_cpus: {
      type: "number",
      label: "Max CPUs",
      default: 4,
      description: "Maximum number of CPUs to use"
    },
    strandedness: {
      type: "select",
      label: "Library Strandedness",
      default: "unstranded",
      options: ["unstranded", "forward", "reverse"],
      description: "Strandedness of RNA-seq library"
    },
    trimming: {
      type: "checkbox",
      label: "Enable Trimming",
      default: true,
      description: "Enable read trimming and adapter removal"
    }
  },
  "Variant Calling": {
    reads: {
      type: "text",
      label: "Input Reads Path",
      default: "s3://sample-data/reads/*.fastq.gz",
      description: "Path to input DNA-seq reads (supports wildcards)"
    },
    reference: {
      type: "text",
      label: "Reference Genome",
      default: "s3://sample-data/reference/genome.fasta",
      description: "Path to reference genome FASTA file"
    },
    outdir: {
      type: "text",
      label: "Output Directory",
      default: "s3://output/variants",
      description: "Path for output results"
    },
    max_memory: {
      type: "text",
      label: "Max Memory",
      default: "16.GB",
      description: "Maximum memory to allocate"
    },
    max_cpus: {
      type: "number",
      label: "Max CPUs",
      default: 4,
      description: "Maximum number of CPUs to use"
    }
  },
  "Metagenomic Analysis": {
    reads: {
      type: "text",
      label: "Input Reads Path",
      default: "s3://sample-data/reads/*.fastq.gz",
      description: "Path to input metagenomic reads (supports wildcards)"
    },
    database: {
      type: "text",
      label: "Reference Database",
      default: "s3://sample-data/reference/metagenomic_db",
      description: "Path to metagenomic reference database"
    },
    outdir: {
      type: "text",
      label: "Output Directory",
      default: "s3://output/metagenomics",
      description: "Path for output results"
    },
    max_memory: {
      type: "text",
      label: "Max Memory",
      default: "32.GB",
      description: "Maximum memory to allocate"
    },
    max_cpus: {
      type: "number",
      label: "Max CPUs",
      default: 8,
      description: "Maximum number of CPUs to use"
    }
  }
};

const PipelineParamsForm = ({ selectedPipelineName, onChange, disabled }) => {
  const [formValues, setFormValues] = useState({});
  const [pipelineSchema, setPipelineSchema] = useState(null);

  // Initial state based on pipeline name
  useEffect(() => {
    if (!selectedPipelineName) {
      setFormValues({});
      setPipelineSchema(null);
      return;
    }
    
    console.log('Pipeline selected:', selectedPipelineName);
    
    // Get the parameter schema for the selected pipeline
    const schema = PIPELINE_PARAMS[selectedPipelineName];
    if (!schema) {
      console.warn(`No parameter schema defined for pipeline: ${selectedPipelineName}`);
      setPipelineSchema(null);
      return;
    }
    
    setPipelineSchema(schema);
    
    // Initialize form with default values
    const defaultValues = {};
    Object.entries(schema).forEach(([key, config]) => {
      defaultValues[key] = config.default;
    });
    
    console.log('Setting default parameter values:', defaultValues);
    setFormValues(defaultValues);
    
    // Notify parent component of the initial values
    onChange(defaultValues);
  }, [selectedPipelineName, onChange]);

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    
    let processedValue = value;
    
    // Process value based on input type
    if (type === 'number') {
      processedValue = value === '' ? '' : Number(value);
    } else if (type === 'checkbox') {
      processedValue = checked;
    }
    
    const updatedValues = {
      ...formValues,
      [name]: processedValue
    };
    
    console.log('Updated form values:', updatedValues);
    setFormValues(updatedValues);
    
    // Notify parent component of the change
    onChange(updatedValues);
  };

  if (!pipelineSchema) {
    return null;
  }

  return (
    <div className="pipeline-params-form">
      <h3>Pipeline Parameters</h3>
      
      {Object.entries(pipelineSchema).map(([paramName, config]) => (
        <div key={paramName} className="form-group">
          <label htmlFor={`param-${paramName}`}>
            {config.label}
          </label>
          
          {config.type === 'text' && (
            <input
              type="text"
              id={`param-${paramName}`}
              value={formValues[paramName] || ''}
              onChange={handleInputChange}
              placeholder={config.default}
              disabled={disabled}
              name={paramName}
            />
          )}
          
          {config.type === 'number' && (
            <input
              type="number"
              id={`param-${paramName}`}
              value={formValues[paramName] || ''}
              onChange={handleInputChange}
              placeholder={config.default}
              disabled={disabled}
              name={paramName}
            />
          )}
          
          {config.type === 'select' && (
            <select
              id={`param-${paramName}`}
              value={formValues[paramName] || ''}
              onChange={handleInputChange}
              disabled={disabled}
              name={paramName}
            >
              {config.options.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          )}
          
          {config.type === 'checkbox' && (
            <div className="checkbox-container">
              <input
                type="checkbox"
                id={`param-${paramName}`}
                checked={Boolean(formValues[paramName])}
                onChange={handleInputChange}
                disabled={disabled}
                name={paramName}
              />
              <label className="checkbox-label" htmlFor={`param-${paramName}`}>
                {config.description}
              </label>
            </div>
          )}
          
          {config.type !== 'checkbox' && (
            <div className="form-hint">{config.description}</div>
          )}
        </div>
      ))}
    </div>
  );
};

export default PipelineParamsForm;
