import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { pipelineApi } from '../../services/api';
import PipelineParamsForm from './PipelineParamsForm';
import './Jobs.css';

const JobSubmission = () => {
  const [pipelines, setPipelines] = useState([]);
  const [selectedPipeline, setSelectedPipeline] = useState('');
  const [selectedPipelineName, setSelectedPipelineName] = useState('');
  const [description, setDescription] = useState('');
  const [params, setParams] = useState({});
  const [loading, setLoading] = useState(false);
  const [fetchingPipelines, setFetchingPipelines] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchPipelines = async () => {
      try {
        setFetchingPipelines(true);
        const response = await pipelineApi.listPipelines();
        // Extract the pipelines array from the response
        if (response && response.pipelines) {
          setPipelines(response.pipelines);
        } else {
          setPipelines([]);
          console.error('Unexpected API response format:', response);
        }
      } catch (err) {
        console.error('Error fetching pipelines:', err);
        setError('Failed to load pipelines. Please try again later.');
      } finally {
        setFetchingPipelines(false);
      }
    };

    fetchPipelines();
  }, []);

  const handlePipelineChange = (e) => {
    const pipelineId = e.target.value;
    setSelectedPipeline(pipelineId);
    
    // Find the pipeline name for the selected pipeline ID
    if (pipelineId) {
      const selected = pipelines.find(p => p.id.toString() === pipelineId.toString());
      setSelectedPipelineName(selected ? selected.name : '');
    } else {
      setSelectedPipelineName('');
    }
  };

  const handleParamsChange = (formValues) => {
    setParams(formValues);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!selectedPipeline) {
      setError('Please select a pipeline');
      return;
    }
    
    try {
      setLoading(true);
      setError(null);
      
      console.log('Submitting job with params:', {
        pipeline_id: selectedPipeline,
        params,
        description
      });
      
      // Ensure params is not empty and is properly structured
      let processedParams = params;
      if (!params || Object.keys(params).length === 0) {
        console.warn('No parameters provided, using empty object');
        processedParams = {};
      }
      
      // Validate each parameter to ensure it's properly formatted
      if (typeof processedParams === 'object') {
        // Remove any null or undefined values
        Object.keys(processedParams).forEach(key => {
          if (processedParams[key] === null || processedParams[key] === undefined) {
            console.warn(`Removing null/undefined parameter: ${key}`);
            delete processedParams[key];
          }
        });
      }
      
      console.log('Processed parameters for submission:', processedParams);
      
      // We're now using the params object directly instead of parsing JSON
      const response = await pipelineApi.submitJob(
        selectedPipeline,
        processedParams, // Use the processed params
        description || '' // Ensure description is never null
      );
      
      console.log('Job submission response:', response);
      
      // Use a timeout to ensure UI updates before redirect
      setTimeout(() => {
        console.log('Redirecting to dashboard...');
        
        // Try multiple redirect approaches to ensure it works
        try {
          // Method 1: Using navigate function from React Router
          navigate('/dashboard', { replace: true });
          
          // Method 2: Direct window location change as fallback
          // This will only happen if the first method fails silently
          setTimeout(() => {
            console.log('Fallback redirect triggered');
            window.location.href = '/dashboard';
          }, 100);
        } catch (navError) {
          console.error('Navigation error:', navError);
          // If navigate fails, use direct location
          window.location.href = '/dashboard';
        }
      }, 300);
      
      // Show success message
      alert('Job submitted successfully! Redirecting to dashboard...');
    } catch (err) {
      console.error('Error submitting job:', err);
      setError(
        err.response?.data?.detail || 
        'Failed to submit job. Please try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="job-submission-container">
      <h1 className="page-title">Submit New Pipeline Job</h1>
      
      {error && <div className="submission-error">{error}</div>}
      
      {fetchingPipelines ? (
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading pipelines...</p>
        </div>
      ) : (
        <div className="submission-card">
          <form onSubmit={handleSubmit} className="submission-form">
            <div className="form-group">
              <label htmlFor="pipeline">Pipeline</label>
              {pipelines.length === 0 ? (
                <div className="empty-pipelines">
                  No pipelines available. Please contact an administrator.
                </div>
              ) : (
                <select
                  id="pipeline"
                  value={selectedPipeline}
                  onChange={handlePipelineChange}
                  disabled={loading}
                  required
                >
                  <option value="">Select a pipeline</option>
                  {pipelines.map((pipeline) => (
                    <option key={pipeline.id} value={pipeline.id}>
                      {pipeline.name}
                    </option>
                  ))}
                </select>
              )}
            </div>
            
            <div className="form-group">
              <label htmlFor="description">Description</label>
              <input
                type="text"
                id="description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Brief job description"
                disabled={loading}
              />
            </div>
            
            {selectedPipelineName && (
              <PipelineParamsForm
                selectedPipelineName={selectedPipelineName}
                onChange={handleParamsChange}
                disabled={loading}
              />
            )}
            
            <div className="form-actions">
              <button
                type="button"
                onClick={() => navigate('/dashboard')}
                className="cancel-action"
                disabled={loading}
              >
                Cancel
              </button>
              <button
                type="submit"
                className="submit-action"
                disabled={loading || pipelines.length === 0}
              >
                {loading ? 'Submitting...' : 'Submit Job'}
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
};

export default JobSubmission;
