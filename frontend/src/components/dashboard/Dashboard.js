import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { pipelineApi } from '../../services/api';
import './Dashboard.css';

const Dashboard = () => {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch jobs on component mount
  useEffect(() => {
    const fetchJobs = async () => {
      try {
        setLoading(true);
        const response = await pipelineApi.listJobs();
        // Check if response exists and handle it properly - even empty arrays are valid
        if (response) {
          setJobs(Array.isArray(response) ? response : []);
          setError(null);
        } else {
          // This case would be unexpected (null/undefined response)
          console.warn('Unexpected response from listJobs API:', response);
          setJobs([]);
          setError(null); // Don't show an error for empty jobs
        }
      } catch (err) {
        console.error('Error fetching jobs:', err);
        setError('Failed to load jobs. Please try again later.');
        // Don't clear jobs array on error to maintain existing data if available
      } finally {
        setLoading(false);
      }
    };

    fetchJobs();
    
    // Set up polling for job status updates every 10 seconds
    const intervalId = setInterval(fetchJobs, 10000);
    
    // Clean up interval on component unmount
    return () => clearInterval(intervalId);
  }, []);

  const handleCancelJob = async (jobId) => {
    if (window.confirm('Are you sure you want to cancel this job?')) {
      try {
        await pipelineApi.cancelJob(jobId);
        // Refresh the job list after cancellation
        const updatedJobs = await pipelineApi.listJobs();
        setJobs(updatedJobs);
      } catch (err) {
        console.error('Error canceling job:', err);
        alert('Failed to cancel job. Please try again.');
      }
    }
  };

  // Helper function to format date
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
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

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h1 className="page-title">Pipeline Jobs Dashboard</h1>
        <Link to="/jobs/new" className="new-job-button">
          + New Job
        </Link>
      </div>

      {error && <div className="dashboard-error">{error}</div>}

      {loading && jobs.length === 0 ? (
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading jobs...</p>
        </div>
      ) : jobs.length === 0 ? (
        <div className="empty-state">
          <h3>No jobs found</h3>
          <p>Start by creating a new pipeline job.</p>
          <Link to="/jobs/new" className="empty-state-button">
            Create First Job
          </Link>
        </div>
      ) : (
        <div className="jobs-table-container">
          <table className="jobs-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Pipeline</th>
                <th>Description</th>
                <th>Status</th>
                <th>Created At</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {jobs.map((job) => (
                <tr key={job.job_id}>
                  <td>
                    <Link to={`/jobs/${job.job_id}`} className="job-id-link">
                      {job.job_id}
                    </Link>
                  </td>
                  <td>{job.pipeline_name || 'Unknown'}</td>
                  <td className="job-description">
                    {job.description || 'No description'}
                  </td>
                  <td>
                    <span className={getStatusBadgeClass(job.status)}>
                      {job.status}
                    </span>
                  </td>
                  <td>{formatDate(job.created_at)}</td>
                  <td>
                    <div className="job-actions">
                      <Link to={`/jobs/${job.job_id}`} className="action-button view-button">
                        View
                      </Link>
                      {['running', 'queued'].includes(job.status?.toLowerCase()) && (
                        <button
                          onClick={() => handleCancelJob(job.job_id)}
                          className="action-button cancel-button"
                        >
                          Cancel
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
