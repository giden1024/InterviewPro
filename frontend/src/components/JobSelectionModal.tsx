import React, { useState, useEffect } from 'react';
import { Job, jobService } from '../services/jobService';

interface JobSelectionModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (selectedJob: Job) => void; // Simplified: only return selected job
  availableJobs?: Job[]; // Optional job list, automatically fetched if not provided
  interviewType?: 'mock' | 'formal'; // Interview type for displaying different titles
}

const JobSelectionModal: React.FC<JobSelectionModalProps> = ({
  isOpen,
  onClose,
  onConfirm,
  availableJobs,
  interviewType = 'mock'
}) => {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');

  // Get job list
  useEffect(() => {
    if (isOpen) {
      fetchJobs();
    }
  }, [isOpen]);

  const fetchJobs = async () => {
    try {
      setLoading(true);
      setError('');

      // Get job data
      const jobsData = availableJobs 
        ? { jobs: availableJobs } 
        : await jobService.getJobs({ per_page: 50 });

      setJobs(jobsData.jobs || []);

      // Auto-select if only one job available
      if (jobsData.jobs && jobsData.jobs.length === 1) {
        setSelectedJob(jobsData.jobs[0]);
      }

      // Check if any jobs are available
      if (!jobsData.jobs || jobsData.jobs.length === 0) {
        setError('No available jobs, please add job information first');
      }

      console.log('JobSelectionModal - Job data loaded successfully:', {
        jobsCount: jobsData.jobs?.length || 0,
        jobs: jobsData.jobs
      });

    } catch (err: any) {
      console.error('Failed to fetch jobs:', err);
      console.error('Error details:', {
        message: err.message,
        stack: err.stack,
        name: err.name
      });
      
      // More detailed error information
      let errorMessage = 'Failed to fetch job data';
      if (err.message?.includes('Failed to fetch')) {
        errorMessage = 'Network connection failed, please check if backend service is running';
      } else if (err.message?.includes('Unauthorized')) {
        errorMessage = 'Login session expired, please log in again';
      } else if (err.message?.includes('404')) {
        errorMessage = 'API endpoint not found, please check backend service';
      } else {
        errorMessage = err.message || 'Unknown error';
      }
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleJobSelect = (job: Job) => {
    setSelectedJob(job);
  };

  const handleConfirm = () => {
    if (selectedJob) {
      onConfirm(selectedJob);
    }
  };

  const handleClose = () => {
    setSelectedJob(null);
    setError('');
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div 
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      style={{ 
        zIndex: 9999,
        display: 'flex',
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100vw',
        height: '100vh',
        backgroundColor: 'rgba(0,0,0,0.5)'
      }}
    >
      <div className="bg-white rounded-xl p-6 w-full max-w-2xl mx-4 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-gray-900">
            Select {interviewType === 'mock' ? 'Mock' : 'Formal'} Interview Position
          </h2>
          <button
            onClick={handleClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {loading && (
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <span className="ml-3 text-gray-600">Loading...</span>
          </div>
        )}

        {error && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-600 text-sm">{error}</p>
            <div className="mt-3 flex space-x-3">
              {error.includes('job') && (
                <button
                  onClick={() => window.open('/jobs', '_blank')}
                  className="text-sm text-blue-600 hover:text-blue-800 underline"
                >
                  Add Job
                </button>
              )}
            </div>
          </div>
        )}

        {!loading && !error && (
          <div className="space-y-6">
            {/* Job selection */}
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-3">Select Target Position</h3>
              <p className="text-sm text-gray-500 mb-4">
                After selecting a position, the system will automatically match the associated resume for {interviewType === 'mock' ? 'mock' : 'formal'} interview
                {interviewType === 'mock' ? ' (8 questions)' : ' (15 questions)'}
              </p>
              <div className="grid grid-cols-1 gap-3 max-h-60 overflow-y-auto">
                {jobs.map((job) => (
                  <div
                    key={job.id}
                    onClick={() => handleJobSelect(job)}
                    className={`border rounded-lg p-4 cursor-pointer transition-all ${
                      selectedJob?.id === job.id
                        ? 'border-blue-500 bg-blue-50 ring-2 ring-blue-200'
                        : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h4 className="font-medium text-gray-900">{job.title}</h4>
                        <p className="text-sm text-gray-600">{job.company}</p>
                        {job.location && (
                          <p className="text-sm text-gray-500 mt-1">📍 {job.location}</p>
                        )}
                        {job.salary_range && (
                          <p className="text-sm text-gray-500">💰 {job.salary_range}</p>
                        )}
                        {job.resume_id && (
                          <p className="text-sm text-green-600 mt-1">✅ Resume Associated</p>
                        )}
                      </div>
                      {selectedJob?.id === job.id && (
                        <div className="text-blue-600">
                          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                          </svg>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Confirm buttons */}
            <div className="flex justify-end space-x-3 pt-4 border-t">
              <button
                onClick={handleClose}
                className="px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleConfirm}
                disabled={!selectedJob}
                className={`px-6 py-2 rounded-lg font-medium transition-colors ${
                  selectedJob
                    ? 'bg-blue-600 text-white hover:bg-blue-700'
                    : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                }`}
              >
                Start Interview
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default JobSelectionModal; 