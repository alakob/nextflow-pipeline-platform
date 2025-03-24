import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { pipelineApi } from '../../services/api';
import './Jobs.css';

const JobSubmission = () => {
  const [pipelines, setPipelines] = useState([]);
  const [selectedPipeline, setSelectedPipeline] = useState('');
  const [description, setDescription] = useState('');
  const [params, setParams] = useState('');
  const [loading, setLoading] = useState(false);
  const [fetchingPipelines, setFetchingPipelines] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchPipelines = async () => {
      try {
        setFetchingPipelines(true);
        const pipelinesData = await pipelineApi.listPipelines();
        setPipelines(pipelinesData);
      } catch (err) {
        console.error('Error fetching pipelines:', err);
        setError('Failed to load pipelines. Please try again later.');
      } finally {
        setFetchingPipelines(false);
      }
    };

    fetchPipelines();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!selectedPipeline) {
      setError('Please select a pipeline');
      return;
    }
    
    try {
      setLoading(true);
      setError(null);
      
      // Parse params from JSON string to object
      let parsedParams;
      try {
        parsedParams = params ? JSON.parse(params) : {};
      } catch (parseErr) {
        setError('Invalid JSON in parameters field');
        setLoading(false);
        return;
      }
      
      const response = await pipelineApi.submitJob(
        selectedPipeline,
        parsedParams,
        description
      );
      
      navigate(`/jobs/${response.id}`);
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
                  onChange={(e) => setSelectedPipeline(e.target.value)}
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
            
            <div className="form-group">
              <label htmlFor="params">
                Parameters (JSON format)
                <span className="optional-label">Optional</span>
              </label>
              <textarea
                id="params"
                value={params}
                onChange={(e) => setParams(e.target.value)}
                placeholder='{"param1": "value1", "param2": "value2"}'
                rows={5}
                disabled={loading}
              />
              <div className="form-hint">
                Enter pipeline parameters in JSON format
              </div>
            </div>
            
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
