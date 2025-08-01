import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { interviewService } from '../services/interviewService';
import { questionService } from '../services/questionService';
import { Job } from '../services/jobService';

interface LocationState {
  jobTitle?: string;
  jobDescription?: string;
  jobId?: string;
  company?: string;
  resumeId?: number;
  resumeText?: string;
  experienceLevel?: string;
  completed?: boolean;
  questionsGenerated?: boolean;
  error?: string;
  selectedJob?: Job;
}

const CompletePage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const state = location.state as LocationState;
  
  const [isLoadingMock, setIsLoadingMock] = useState(false);
  const [isLoadingFormal, setIsLoadingFormal] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [taskId, setTaskId] = useState<string | null>(null);
  const [taskProgress, setTaskProgress] = useState<{
    current: number;
    total: number;
    status: string;
  } | null>(null);

  // Handle interview selection
  const handleStartInterview = async (interviewType: 'mock' | 'formal') => {
    if (!state.resumeId) {
      setError('Resume information missing, please re-upload your resume');
      return;
    }

    // Set loading state for corresponding button
    if (interviewType === 'mock') {
      setIsLoadingMock(true);
    } else {
      setIsLoadingFormal(true);
    }
    
    setError(null);

    try {
      // Create interview session
      const session = await interviewService.createInterview({
        resume_id: state.resumeId,
        interview_type: interviewType === 'mock' ? 'mock' : 'comprehensive',
        total_questions: interviewType === 'mock' ? 8 : 15,
        custom_title: `${state.jobTitle || 'Interview'} - ${interviewType === 'mock' ? 'Mock' : 'Formal'} Interview`
      });

      // Generate interview questions
      const questionData = {
        resume_id: state.resumeId,
        session_id: session.session_id,
        interview_type: 'comprehensive' as const,
        total_questions: interviewType === 'mock' ? 8 : 15
      };

      // Use synchronous question generation API
      const result = await questionService.generateQuestions(questionData);
      
      // Handle result directly, synchronous API returns question data directly
      if (result.questions && result.questions.length > 0) {
        // Questions generated successfully, navigate to interview page
        navigate(interviewType === 'mock' ? '/mock-interview' : '/interview', {
          state: { 
            sessionId: session.session_id,
            questions: result.questions,
            jobTitle: state.jobTitle,
            company: state.company
          }
        });
      } else {
        setError('Question generation failed, please try again');
      }
    } catch (error: any) {
      console.error('Failed to create interview:', error);
      setError(error.message || 'Failed to create interview, please try again');
    } finally {
      // Clear loading state
      setIsLoadingMock(false);
      setIsLoadingFormal(false);
    }
  };

  // Return to home page
  const goHome = () => {
    navigate('/home');
  };

  return (
    <div className="min-h-screen" style={{ backgroundColor: '#EEF9FF' }}>
      <div className="container mx-auto px-6 max-w-4xl py-12">
        
        {/* Success notification area */}
        <div className="bg-white rounded-2xl shadow-sm p-8 mb-8">
          <div className="text-center">
            <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <svg className="w-10 h-10 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
            </div>
            <h1 className="text-3xl font-bold text-gray-800 mb-4">
              ✅ Resume Upload Successful!
            </h1>
            <p className="text-gray-600 text-lg mb-6">
              Your resume has been successfully parsed and saved to the system.
            </p>
            
            {/* Job information display */}
            {state.jobTitle && (
              <div className="inline-block bg-blue-50 px-6 py-3 rounded-xl border border-blue-200">
                <div className="text-blue-800 font-medium text-lg">{state.jobTitle}</div>
                {state.company && (
                  <div className="text-blue-600 text-sm">{state.company}</div>
                )}
                {state.experienceLevel && (
                  <div className="text-blue-600 text-sm">{state.experienceLevel} Level</div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Error notification */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-6 mb-8">
            <div className="flex items-center space-x-3">
              <svg className="w-6 h-6 text-red-600" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
              <div className="text-red-700 font-medium">{error}</div>
            </div>
          </div>
        )}

        {/* Task progress display */}
        {taskProgress && (
          <div className="bg-blue-50 border border-blue-200 rounded-xl p-6 mb-8">
            <div className="flex items-center space-x-3 mb-4">
              <svg className="w-6 h-6 text-blue-600 animate-spin" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clipRule="evenodd" />
              </svg>
              <div className="text-blue-700 font-medium">Generating interview questions...</div>
            </div>
            
            <div className="mb-3">
              <div className="flex justify-between text-sm text-blue-600 mb-1">
                <span>Progress</span>
                <span>{taskProgress.current}%</span>
              </div>
              <div className="w-full bg-blue-200 rounded-full h-2">
                <div 
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${taskProgress.current}%` }}
                ></div>
              </div>
            </div>
            
            <div className="text-sm text-blue-600">
              {taskProgress.status}
            </div>
          </div>
        )}

        {/* Interview selection area */}
        <div className="bg-white rounded-2xl shadow-sm p-8 mb-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-6 text-center">
            Choose Interview Type
          </h2>
          
          <div className="grid md:grid-cols-2 gap-6">
            {/* Mock interview option */}
            <div className="border-2 border-gray-200 rounded-xl p-6 hover:border-blue-300 transition-colors">
              <div className="text-center mb-4">
                <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
                  <span className="text-2xl">🎯</span>
                </div>
                <h3 className="text-xl font-semibold text-gray-800 mb-2">Mock Interview</h3>
                <p className="text-gray-600 text-sm mb-4">Quick practice to familiarize with the interview process</p>
              </div>
              
              <div className="space-y-2 mb-6">
                <div className="flex items-center text-sm text-gray-600">
                  <span className="w-2 h-2 bg-blue-500 rounded-full mr-2"></span>
                  8 curated questions
                </div>
                <div className="flex items-center text-sm text-gray-600">
                  <span className="w-2 h-2 bg-blue-500 rounded-full mr-2"></span>
                  Quick feedback and scoring
                </div>
                <div className="flex items-center text-sm text-gray-600">
                  <span className="w-2 h-2 bg-blue-500 rounded-full mr-2"></span>
                  Perfect for first-time experience
                </div>
              </div>
              
              <button
                onClick={() => handleStartInterview('mock')}
                disabled={isLoadingMock || isLoadingFormal}
                className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoadingMock ? 'Creating...' : 'Start Mock Interview'}
              </button>
            </div>

            {/* Formal interview option */}
            <div className="border-2 border-gray-200 rounded-xl p-6 hover:border-green-300 transition-colors">
              <div className="text-center mb-4">
                <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3">
                  <span className="text-2xl">📋</span>
                </div>
                <h3 className="text-xl font-semibold text-gray-800 mb-2">Formal Interview</h3>
                <p className="text-gray-600 text-sm mb-4">Comprehensive assessment with in-depth analysis</p>
              </div>
              
              <div className="space-y-2 mb-6">
                <div className="flex items-center text-sm text-gray-600">
                  <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                  15 comprehensive questions
                </div>
                <div className="flex items-center text-sm text-gray-600">
                  <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                  Detailed capability analysis
                </div>
                <div className="flex items-center text-sm text-gray-600">
                  <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                  Professional assessment report
                </div>
              </div>
              
              <button
                onClick={() => handleStartInterview('formal')}
                disabled={isLoadingFormal || isLoadingMock}
                className="w-full px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoadingFormal ? 'Creating...' : 'Start Formal Interview'}
              </button>
            </div>
          </div>
        </div>

        {/* Return to home option */}
        <div className="bg-white rounded-2xl shadow-sm p-8">
          <div className="text-center">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">
              Or start interview later
            </h3>
            <p className="text-gray-600 mb-6">
              You can restart the interview anytime from the home page
            </p>
            <button
              onClick={goHome}
              className="px-8 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
            >
              🏠 Return to Home
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CompletePage; 