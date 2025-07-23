import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

interface LocationState {
  sessionId?: string;
  jobTitle?: string;
  jobId?: string;
  resumeId?: number;
  completed?: boolean;
  totalQuestions?: number;
  answeredQuestions?: number;
  duration?: number;
  questionsGenerated?: boolean;
  experienceLevel?: string;
  error?: string;
}

const CompletePage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { 
    sessionId, 
    jobTitle, 
    jobId, 
    resumeId, 
    completed, 
    totalQuestions, 
    answeredQuestions, 
    duration,
    questionsGenerated,
    experienceLevel,
    error: stateError
  } = (location.state as LocationState) || {};

  // Start new interview
  const startNewInterview = () => {
    navigate('/mock-interview');
  };

  // Return to home
  const goHome = () => {
    navigate('/home');
  };

  // View interview records (function disabled as buttons are hidden)
  // const viewInterviewHistory = () => {
  //   navigate('/profile', { state: { activeTab: 'interviews' } });
  // };

  // Format duration
  const formatDuration = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
      return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="min-h-screen bg-gray-100 py-8">
      <div className="container mx-auto px-6 max-w-4xl">
        {/* Header */}
        <div className="bg-white rounded-xl shadow-sm p-8 mb-8">
          <div className="text-center">
            <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-10 h-10 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
            </div>
            <h1 className="text-3xl font-bold text-gray-800 mb-2">
              {completed ? 'Interview Complete!' : 'Interview Preparation Complete!'}
            </h1>
            <p className="text-gray-600 mb-6">
              {completed 
                ? 'Congratulations on completing your interview, thank you for participating' 
                : 'Your interview preparation is complete, you can now start the formal interview'}
            </p>
            
            {jobTitle && (
              <div className="inline-block bg-blue-50 px-4 py-2 rounded-lg">
                <span className="text-blue-600 font-medium">{jobTitle}</span>
              </div>
            )}
          </div>
        </div>

        {/* Error Display */}
        {stateError && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-8">
            <div className="flex items-start space-x-3">
              <svg className="w-5 h-5 text-red-600 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
              <div className="flex-1">
                <div className="text-red-700 font-medium mb-2">Operation Failed</div>
                <div className="text-red-600 text-sm mb-3">{stateError}</div>
                
                {/* Action buttons */}
                <div className="flex flex-wrap gap-2">
                  <button
                    onClick={() => navigate('/home')}
                    className="px-3 py-1 bg-gray-600 text-white text-sm rounded hover:bg-gray-700 transition-colors"
                  >
                    Return Home
                  </button>
                  {/* View Interview Records button hidden as requested */}
                  {/* <button
                    onClick={() => navigate('/profile', { state: { activeTab: 'interviews' } })}
                    className="px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 transition-colors"
                  >
                    View Interview Records
                  </button> */}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Success Messages */}
        {questionsGenerated && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-8">
            <div className="flex items-center space-x-2">
              <svg className="w-5 h-5 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              <div className="text-green-700">
                <strong>Preparation Complete!</strong> Successfully generated {totalQuestions || 8} interview questions
                {jobId && <span>, job information has been saved</span>}
              </div>
            </div>
          </div>
        )}

        {/* Interview Summary */}
        {completed && (
          <div className="bg-white rounded-xl shadow-sm p-8 mb-8">
            <h2 className="text-xl font-semibold text-gray-800 mb-6">Interview Overview</h2>
            
            <div className="grid grid-cols-2 md:grid-cols-3 gap-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">{answeredQuestions || 0}</div>
                <div className="text-sm text-gray-600">Answered Questions</div>
                <div className="text-xs text-gray-500">/ {totalQuestions || 0} questions</div>
              </div>
              
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {duration ? formatDuration(duration) : '00:00'}
                </div>
                <div className="text-sm text-gray-600">Interview Duration</div>
              </div>

              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">
                  {sessionId ? 'Completed' : 'Preparing'}
                </div>
                <div className="text-sm text-gray-600">Status</div>
              </div>
            </div>
          </div>
        )}

        {/* Session Information */}
        {sessionId && (
          <div className="bg-white rounded-xl shadow-sm p-8 mb-8">
            <h2 className="text-xl font-semibold text-gray-800 mb-6">Session Information</h2>
            
            <div className="space-y-4">
              <div className="flex items-center justify-between py-3 border-b border-gray-100">
                <span className="text-gray-600">Session ID</span>
                <span className="text-gray-800 font-mono text-sm">{sessionId}</span>
              </div>
              
              {jobTitle && (
                <div className="flex items-center justify-between py-3 border-b border-gray-100">
                  <span className="text-gray-600">Position</span>
                  <span className="text-gray-800">{jobTitle}</span>
                </div>
              )}
              
              {experienceLevel && (
                <div className="flex items-center justify-between py-3 border-b border-gray-100">
                  <span className="text-gray-600">Experience Level</span>
                  <span className="text-gray-800">{experienceLevel}</span>
                </div>
              )}
              
              {resumeId && (
                <div className="flex items-center justify-between py-3 border-b border-gray-100">
                  <span className="text-gray-600">Resume ID</span>
                  <span className="text-gray-800">#{resumeId}</span>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="bg-white rounded-xl shadow-sm p-8">
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button
              onClick={goHome}
              className="px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors flex items-center justify-center space-x-2"
            >
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z"/>
              </svg>
              <span>Return Home</span>
            </button>

            {/* View History button hidden as requested */}
            {/* <button
              onClick={viewInterviewHistory}
              className="px-6 py-3 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-colors"
            >
              View History
            </button> */}
            
            <button
              onClick={startNewInterview}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Start New Interview
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CompletePage; 