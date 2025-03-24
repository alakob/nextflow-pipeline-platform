import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { pipelineApi } from '../../services/api';
import './Jobs.css';

const JobDetail = () => {
  const { jobId } = useParams();
  const navigate = useNavigate();
  const [job, setJob] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [downloadLink, setDownloadLink] = useState(null);
  const [downloadLoading, setDownloadLoading] = useState(false);
  const [downloadError, setDownloadError] = useState(null);

  useEffect(() => {
    // Define fetchJobDetails inside useEffect to prevent dependency issues
    const fetchJobDetails = async () => {
      try {
        setLoading(true);
        console.log('JobDetail component - Fetching job with ID:', jobId);
        
        const jobData = await pipelineApi.getJobStatus(jobId);
        
        if (jobData) {
          console.log('JobDetail component - Received job data:', jobData);
          console.log('JobDetail component - Params field:', jobData.params);
          console.log('JobDetail component - Params type:', typeof jobData.params);
          setJob(jobData);
          setError(null);
          
          // If job is completed, attempt to get the download link
          if (jobData.status.toLowerCase() === 'completed') {
            fetchDownloadLink();
          }
        } else {
          console.error('JobDetail component - Received empty job data');
          setError('No job data found. The job may not exist or has been deleted.');
        }
      } catch (err) {
        console.error('JobDetail component - Error fetching job details:', err);
        const errorMessage = err.response?.status === 404 
          ? `Job with ID ${jobId} not found. It may have been deleted or never existed.`
          : 'Failed to load job details. Please try again later.';
        
        setError(errorMessage);
        
        // Use navigate on critical errors - after a delay
        if (err.response?.status === 404) {
          setTimeout(() => {
            navigate('/dashboard');
          }, 3000);
        }
      } finally {
        setLoading(false);
      }
    };

    const fetchDownloadLink = async () => {
      try {
        setDownloadLoading(true);
        setDownloadError(null);
        const linkData = await pipelineApi.getJobDownloadLink(jobId);
        setDownloadLink(linkData.download_url);
      } catch (err) {
        console.error('Error fetching download link:', err);
        setDownloadError('Could not generate download link for this job.');
      } finally {
        setDownloadLoading(false);
      }
    };

    if (jobId) {
      fetchJobDetails();
    } else {
      setError('Invalid job ID provided');
      setLoading(false);
    }
    
    // Set up polling for job status updates every 5 seconds if job is in an active state
    const intervalId = setInterval(() => {
      if (job && ['running', 'queued', 'submitted'].includes(job.status?.toLowerCase())) {
        fetchJobDetails();
      }
    }, 5000);
    
    // Clean up interval on component unmount
    return () => clearInterval(intervalId);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [jobId, navigate]);

  const handleCancelJob = async () => {
    if (window.confirm('Are you sure you want to cancel this job?')) {
      try {
        await pipelineApi.cancelJob(jobId);
        // Refetch job details after cancellation
        const updatedJob = await pipelineApi.getJobStatus(jobId);
        setJob(updatedJob);
      } catch (err) {
        console.error('Error canceling job:', err);
        alert('Failed to cancel job. Please try again.');
      }
    }
  };

  const handleDownload = () => {
    // If the download link exists, open it in a new tab
    if (downloadLink) {
      window.open(downloadLink, '_blank');
    } else {
      alert('Download link is not available.');
    }
  };

  // Helper function to format date
  const formatDate = (dateString) => {
    return dateString ? new Date(dateString).toLocaleString() : 'N/A';
  };

  // Helper function to get status badge class
  const getStatusBadgeClass = (status) => {
    switch (status.toLowerCase()) {
      case 'running':
        return 'status-badge status-running';
      case 'completed':
        return 'status-badge status-completed';
      case 'failed':
        return 'status-badge status-failed';
      case 'canceled':
        return 'status-badge status-canceled';
      case 'queued':
        return 'status-badge status-queued';
      default:
        return 'status-badge';
    }
  };

  // Function to properly display job parameters 
  const displayJobParameters = () => {
    if (!job) return 'None';
    
    console.log('[JobDetail] Full job data:', job);
    
    // Check if job.params exists
    if (!job.params) {
      console.log('[JobDetail] No params field in job object');
      return 'None';
    }
    
    console.log('[JobDetail] Job params field type:', typeof job.params);
    console.log('[JobDetail] Job params field value:', job.params);
    
    try {
      // If params is an empty object or null/undefined
      if (!job.params || 
          (typeof job.params === 'object' && Object.keys(job.params).length === 0) ||
          job.params === '{}') {
        console.log('[JobDetail] Empty parameters detected');
        return 'None';
      }
      
      // If params is a non-empty object, format it nicely
      if (typeof job.params === 'object') {
        console.log('[JobDetail] Processing parameters as object');
        // Convert parameters with default values back to a clean object
        const cleanParams = {};
        Object.entries(job.params).forEach(([key, value]) => {
          console.log(`[JobDetail] Processing parameter ${key} with value:`, value);
          // Filter out null/undefined values
          if (value !== null && value !== undefined) {
            cleanParams[key] = value;
          }
        });
        
        // Only show 'None' if after cleaning we have no parameters
        if (Object.keys(cleanParams).length === 0) {
          console.log('[JobDetail] No valid parameters after cleaning');
          return 'None';
        }
        
        console.log('[JobDetail] Final cleaned parameters:', cleanParams);
        // Convert object to JSON string for React rendering
        return (
          <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
            {JSON.stringify(cleanParams, null, 2)}
          </pre>
        );
      }
      
      // If params is a string, try to parse it as JSON
      if (typeof job.params === 'string') {
        try {
          // Handle empty JSON string
          if (job.params.trim() === '{}' || job.params.trim() === '') {
            return 'None';
          }
          
          const parsedParams = JSON.parse(job.params);
          
          // If parsed params is empty, return None
          if (Object.keys(parsedParams).length === 0) {
            return 'None';
          }
          
          return (
            <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
              {JSON.stringify(parsedParams, null, 2)}
            </pre>
          );
        } catch (e) {
          console.log('[JobDetail] Could not parse params as JSON string:', e);
          // If not empty string but not JSON, show as raw string
          return job.params.trim() ? <pre>{job.params}</pre> : 'None';
        }
      }
      
      // Fallback for any other type - ensure we convert to string
      return <pre>{String(job.params || '')}</pre>;
      
    } catch (error) {
      console.error('[JobDetail] Error displaying job parameters:', error);
      return 'Error displaying parameters';
    }
  };

  return (
    <div className="job-detail-container">
      <div className="detail-header">
        <h1 className="page-title">Job Details</h1>
        <Link to="/dashboard" className="back-button">
          Back to Dashboard
        </Link>
      </div>

      {error && <div className="detail-error">{error}</div>}

      {loading && !job ? (
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading job details...</p>
        </div>
      ) : job ? (
        <div className="detail-card">
          <div className="detail-section">
            <div className="detail-header-info">
              <h2>Job ID: {job.id}</h2>
              <span className={getStatusBadgeClass(job.status)}>
                {job.status}
              </span>
            </div>
            
            <div className="job-timeline">
              <div className="timeline-event">
                <div className="timeline-icon timeline-created"></div>
                <div className="timeline-content">
                  <span className="timeline-label">Created:</span>
                  <span className="timeline-time">{formatDate(job.created_at)}</span>
                </div>
              </div>
              
              {job.started_at && (
                <div className="timeline-event">
                  <div className="timeline-icon timeline-started"></div>
                  <div className="timeline-content">
                    <span className="timeline-label">Started:</span>
                    <span className="timeline-time">{formatDate(job.started_at)}</span>
                  </div>
                </div>
              )}
              
              {job.completed_at && (
                <div className="timeline-event">
                  <div className="timeline-icon timeline-completed"></div>
                  <div className="timeline-content">
                    <span className="timeline-label">Completed:</span>
                    <span className="timeline-time">{formatDate(job.completed_at)}</span>
                  </div>
                </div>
              )}
            </div>
            
            <div className="detail-metadata">
              <div className="metadata-item">
                <span className="metadata-label">Pipeline:</span>
                <span className="metadata-value">{job.pipeline_name || 'Unknown'}</span>
              </div>
              
              <div className="metadata-item">
                <span className="metadata-label">Description:</span>
                <span className="metadata-value">{job.description || 'No description'}</span>
              </div>
            </div>
          </div>
          
          <div className="detail-section">
            <h3>Parameters</h3>
            <div className="parameters-json">
              {displayJobParameters()}
            </div>
          </div>
          
          <div className="detail-actions">
            {/* Download button for completed jobs */}
            {job.status.toLowerCase() === 'completed' && (
              <div className="download-section">
                <h3>Download Results</h3>
                {downloadLoading ? (
                  <div className="loading-container">
                    <div className="loading-spinner"></div>
                    <p>Generating download link...</p>
                  </div>
                ) : downloadError ? (
                  <div className="download-error">{downloadError}</div>
                ) : downloadLink ? (
                  <button
                    onClick={handleDownload}
                    className="download-button"
                  >
                    Download Analysis Results
                  </button>
                ) : (
                  <p>No download available for this job.</p>
                )}
              </div>
            )}
            
            {/* Cancel button for running jobs */}
            {['running', 'queued'].includes(job.status.toLowerCase()) && (
              <button
                onClick={handleCancelJob}
                className="cancel-job-button"
              >
                Cancel Job
              </button>
            )}
          </div>
        </div>
      ) : (
        <div className="not-found">
          <h2>Job not found</h2>
          <p>The requested job could not be found.</p>
          <Link to="/dashboard" className="back-button">
            Back to Dashboard
          </Link>
        </div>
      )}
    </div>
  );
};

export default JobDetail;
