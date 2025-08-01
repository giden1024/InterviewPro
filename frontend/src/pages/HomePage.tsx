import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUserInfo } from '../hooks/useUserInfo';
import { useHomePage } from '../hooks/useHomePage';
import { useInterviewRecord, InterviewRecord } from '../hooks/useInterviewRecord';
import { useAuthRedirect } from '../hooks/useAuthRedirect';
import { jobService, Job } from '../services/jobService';
import { questionService, Question } from '../services/questionService';
import { interviewService, InterviewSession } from '../services/interviewService';
import { resumeService, Resume } from '../services/resumeService';
import { formatUserDisplayId } from '../utils/userUtils';
import JobSelectionModal from '../components/JobSelectionModal';
import logoImg from '../assets/logo02.png';

interface DashboardStats {
  totalJobs: number;
  totalQuestions: number;
  totalInterviews: number;
  completedInterviews: number;
}

const HomePage: React.FC = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('questions');
  const { user, isLoading: userLoading, error: userError, fetchUserInfo } = useUserInfo();
  const { 
    questionsWithAnswers, 
    isLoading: questionsLoading, 
    error: questionsError,
    isGeneratingQuestions,
    handleQuestionEdit,
    handleQuestionDelete,
    loadQuestionsWithAnswers,
    generateNewQuestions
  } = useHomePage();
  
  // Interview record management
  const {
    records,
    loading: recordsLoading,
    error: recordsError,
    refreshRecords,
    deleteRecord
  } = useInterviewRecord();
  
  // Authentication redirect handling
  const { handleApiError } = useAuthRedirect();
  
  // Image error handling
  const handleImageError = (e: React.SyntheticEvent<HTMLImageElement, Event>) => {
    const target = e.target as HTMLImageElement;
    target.style.display = 'none';
    const parent = target.parentElement;
    if (parent) {
      parent.style.backgroundColor = '#77C3FF';
      parent.innerHTML = '<div class="w-full h-full flex items-center justify-center text-white font-semibold">Image</div>';
    }
  };
  
  // State management
  const [jobs, setJobs] = useState<Job[]>([]);
  const [questions, setQuestions] = useState<Question[]>([]);
  const [interviews, setInterviews] = useState<InterviewSession[]>([]);
  const [stats, setStats] = useState<DashboardStats>({
    totalJobs: 0,
    totalQuestions: 0,
    totalInterviews: 0,
    completedInterviews: 0
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');
  
  // Job selection modal state
  const [isJobModalOpen, setIsJobModalOpen] = useState(false);
  const [interviewType, setInterviewType] = useState<'mock' | 'formal'>('mock');

  // Interview review states
  const [selectedInterviewRecord, setSelectedInterviewRecord] = useState<InterviewRecord | null>(null);
  const [showInterviewDetail, setShowInterviewDetail] = useState(false);
  const [showFullDetails, setShowFullDetails] = useState(false);
  const [interviewFullData, setInterviewFullData] = useState<any>(null);
  const [loadingFullDetails, setLoadingFullDetails] = useState(false);

  // Fetch data when page loads
  useEffect(() => {
    fetchUserInfo();
    loadDashboardData();
    // loadQuestionsWithAnswers() 由 useHomePage hook 自动调用
  }, []);

  // Load dashboard data
  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError('');

      // Load data in parallel
      const [jobsRes, questionsRes, interviewsRes] = await Promise.all([
        jobService.getJobs({ per_page: 10 }),
        questionService.getQuestions({ per_page: 10 }),
        interviewService.getInterviews({ per_page: 10 })
      ]);

      setJobs(jobsRes.jobs || []);
      setQuestions(questionsRes.questions || []);
      setInterviews(interviewsRes.sessions || []);

      // Calculate statistics
      setStats({
        totalJobs: jobsRes.jobs?.length || 0,
        totalQuestions: questionsRes.pagination?.total || 0,
        totalInterviews: interviewsRes.sessions?.length || 0,
        completedInterviews: interviewsRes.sessions?.filter((i: InterviewSession) => i.status === 'completed').length || 0
      });

    } catch (err) {
      console.error('Failed to load dashboard data:', err);
      
      // 使用统一的错误处理
      handleApiError(err);
      
      setError('Failed to load data, please refresh and try again');
    } finally {
      setLoading(false);
    }
  };

  // Add new job
  const handleAddNewJob = () => {
    navigate('/jobs');
  };

  // Select job
  const handleSelectJob = async (job: Job) => {
    try {
      let resumeId = job.resume_id;
      
      // 如果job没有关联简历，获取用户的第一个已处理简历
      if (!resumeId) {
        console.log('Job has no associated resume, fetching user resumes...');
        const resumesResponse = await resumeService.getResumes({ per_page: 50 });
        const allResumes = (resumesResponse as any)?.data?.resumes || resumesResponse?.resumes || [];
        const processedResumes = allResumes.filter((resume: Resume) => 
          resume.status === 'completed' || resume.status === 'processed'
        );
        
        if (processedResumes.length === 0) {
          alert('No processed resume available. Please upload a resume and wait for processing to complete.');
          navigate('/resume');
          return;
        }
        
        resumeId = processedResumes[0].id;
        console.log('Using resume:', resumeId);
      }
      
      navigate('/complete', { 
        state: { 
          jobTitle: job.title,
          jobDescription: job.description,
          jobId: job.id.toString(),
          company: job.company,
          resumeId: resumeId, // 确保有有效的resumeId
          experienceLevel: job.experience_level,
          selectedJob: job
        } 
      });
    } catch (error) {
      console.error('Error selecting job:', error);
      alert('Failed to get job information. Please try again.');
    }
  };

  // Start mock interview - open job selection modal
  const handleStartMockInterview = () => {
    console.log('🎯 Mock Interview button clicked');
    console.log('Current token:', localStorage.getItem('access_token'));
    console.log('Setting Modal state to true');
    setInterviewType('mock');
    setIsJobModalOpen(true);
    console.log('Modal state set, isJobModalOpen should be true');
  };

  // Handle job selection confirmation - navigate to different pages based on interview type
  const handleJobSelectionConfirm = async (selectedJob: Job) => {
    try {
      setIsJobModalOpen(false);
      
      // Get associated resume
      let resumeId = selectedJob.resume_id;
      
      // If the job has no associated resume, get the user's first processed resume
      if (!resumeId) {
        const resumesResponse = await resumeService.getResumes({ per_page: 50 });
        const allResumes = (resumesResponse as any)?.data?.resumes || resumesResponse?.resumes || [];
        const processedResumes = allResumes.filter((resume: Resume) => 
          resume.status === 'completed' || resume.status === 'processed'
        );
        
        if (processedResumes.length === 0) {
                  alert('No processed resumes available, please upload and wait for resume processing to complete');
        navigate('/resume');
          return;
        }
        
        resumeId = processedResumes[0].id;
      }
      
      // Set different parameters based on interview type
      const isMockInterview = interviewType === 'mock';
      const totalQuestions = isMockInterview ? 8 : 15;
      const titleSuffix = isMockInterview ? 'Mock Interview' : 'Formal Interview';
      
      // Create new interview session
      const session = await interviewService.createInterview({
        resume_id: resumeId!,
        interview_type: 'comprehensive',
        total_questions: totalQuestions,
        custom_title: `${selectedJob.title} @ ${selectedJob.company} ${titleSuffix}`
      });
      
      // Navigate to different pages based on interview type
      if (isMockInterview) {
        navigate('/mock-interview', { 
          state: { 
            sessionId: session.session_id,
            selectedJob: selectedJob,
            resumeId: resumeId
          } 
        });
      } else {
        navigate('/interview', { 
          state: { 
            sessionId: session.session_id,
            selectedJob: selectedJob,
            resumeId: resumeId
          } 
        });
      }
    } catch (err) {
      console.error('Failed to create interview:', err);
      alert('Failed to create interview, please try again later');
    }
  };

  // Close job selection modal
  const handleJobModalClose = () => {
    setIsJobModalOpen(false);
    setInterviewType('mock'); // Reset to default value
  };

  // Start formal interview - consistent logic with Mock Interview
  const handleStartFormalInterview = () => {
    console.log('🎯 Formal Interview button clicked');
    console.log('Current token:', localStorage.getItem('access_token'));
    console.log('Setting Modal state to true');
    setInterviewType('formal');
    setIsJobModalOpen(true);
    console.log('Modal state set, isJobModalOpen should be true');
  };

  // Edit question
  const handleEditQuestion = (questionId: string) => {
    navigate(`/questions/${questionId}/edit`);
  };

  // Delete question
  const handleDeleteQuestion = async (questionId: string | number) => {
    if (!confirm('Are you sure you want to delete this question?')) return;

    try {
      await questionService.deleteQuestion(Number(questionId));
      // Reload questions and answers data
      loadQuestionsWithAnswers();
    } catch (err) {
      console.error('Failed to delete question:', err);
      alert('Delete failed, please try again later');
    }
  };

  // Handle interview review
  const handleReviewInterview = (record: InterviewRecord) => {
    setSelectedInterviewRecord(record);
    setShowInterviewDetail(true);
  };

  const handleCloseInterviewDetail = () => {
    setShowInterviewDetail(false);
    setSelectedInterviewRecord(null);
    setShowFullDetails(false);
    setInterviewFullData(null);
  };

  // Handle view full details
  const handleViewFullDetails = async () => {
    if (!selectedInterviewRecord) return;
    
    try {
      setLoadingFullDetails(true);
      
      console.log('Fetching details for session:', selectedInterviewRecord.session.session_id);
      
      // 获取面试详情和答案
      const [interviewData, answersData] = await Promise.all([
        interviewService.getInterview(selectedInterviewRecord.session.session_id),
        interviewService.getInterviewAnswers(selectedInterviewRecord.session.session_id)
      ]);
      
      console.log('Interview data:', interviewData);
      console.log('Answers data:', answersData);
      
      setInterviewFullData({
        ...interviewData,
        answers: answersData
      });
      setShowFullDetails(true);
      
    } catch (error: any) {
              console.error('Failed to get interview details:', error);
        console.error('Error details:', error);
        alert(`Failed to get interview details: ${error.message || 'Please try again'}`);
    } finally {
      setLoadingFullDetails(false);
    }
  };

  // Redirect to login page if user is not logged in
  useEffect(() => {
    if (!userLoading && !user && !userError) {
      navigate('/login');
    }
  }, [user, userLoading, userError, navigate]);

  if (userLoading || loading) {
    return (
      <div className="min-h-screen bg-[#EEF9FF] flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-[#68C6F1] border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-[#3D3D3D]">Loading...</p>
        </div>
      </div>
    );
  }

  if (userError) {
    return (
      <div className="min-h-screen bg-[#EEF9FF] flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-500 mb-4">❌ {userError}</div>
          <button
            onClick={() => navigate('/login')}
            className="px-6 py-2 bg-[#68C6F1] text-white rounded-lg hover:bg-[#5AB5E0] transition-colors"
          >
            Login Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#EEF9FF] flex">
      {/* Left Sidebar */}
      <div className="w-60 bg-white shadow-lg">
        {/* Logo */}
        <div className="p-6 border-b">
          <div className="flex items-center">
            <img src={logoImg} alt="OfferOtter Logo" className="w-10 h-10 mr-3" />
            <span className="text-xl font-bold text-[#282828]">Offerotter</span>
          </div>
        </div>

        {/* Add New Jobs Card */}
        <div className="p-4">
          <div 
            className="border-2 border-dashed border-[#77C3FF] rounded-2xl p-6 text-center bg-[#EEF9FF] cursor-pointer hover:bg-[#E0F7FF] transition-colors"
            onClick={handleAddNewJob}
          >
            <div className="w-12 h-12 bg-gradient-to-r from-[#9CFAFF] to-[#6BBAFF] rounded-xl mx-auto mb-3 flex items-center justify-center">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
            </div>
            <h3 className="font-medium text-[#282828] text-sm">Add New Jobs</h3>
          </div>
        </div>

        {/* Jobs List */}
        <div className="px-4 pb-4">
          <h3 className="text-[#282828] font-medium mb-3">Jobs ({jobs.length})</h3>
          <div className="space-y-2 max-h-40 overflow-y-auto">
            {jobs.length > 0 ? (
              jobs.map((job) => (
                <div 
                  key={job.id}
                  className="p-3 bg-white border border-transparent rounded-xl cursor-pointer hover:border-[#68C6F1] hover:shadow-sm transition-all"
                  onClick={() => handleSelectJob(job)}
                >
                  <div className="text-[#282828] text-sm font-medium truncate">{job.title}</div>
                  <div className="text-[#666] text-xs truncate">{job.company}</div>
                </div>
              ))
            ) : (
              <div className="text-[#666] text-sm text-center py-4">
                No jobs yet, click above to add
              </div>
            )}
          </div>
        </div>

        {/* User Profile */}
        <div className="absolute bottom-0 left-0 right-0 w-60 p-4 bg-[#EBF8FF] border-t">
          <div className="flex items-center mb-4">
            <div className="w-10 h-10 rounded-full overflow-hidden bg-gradient-to-r from-[#9CFAFF] to-[#6BBAFF] flex items-center justify-center mr-3">
              {user?.avatar_url ? (
                <img 
                  src={user.avatar_url} 
                  alt={user.username || user.email}
                  className="w-full h-full object-cover"
                />
              ) : (
                <span className="text-white font-semibold text-sm">
                  {user ? (user.username || user.email).charAt(0).toUpperCase() : 'U'}
                </span>
              )}
            </div>
            <div className="flex-1">
              <div className="text-sm font-medium text-[#262626]">
                {user?.username || user?.email || 'Guest'}
              </div>
              <div className="text-xs text-[#333333]">
                {user ? formatUserDisplayId(user.id) : 'Not logged in'}
              </div>
            </div>
            <div className="bg-white px-3 py-1 rounded-full text-xs text-[#3D3D3D] shadow-sm">
              Free
            </div>
          </div>
          <button 
            onClick={() => navigate('/profile')}
            className="w-full py-2 bg-gradient-to-r from-[#9CFAFF] to-[#6BBAFF] text-white rounded-full text-sm font-medium hover:shadow-lg transition-all"
          >
            Upgrade
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 p-6">
        {/* Top Interview Cards Section - Added based on design */}
        <div className="flex gap-6 mb-6">
          {/* Mock Interview Card */}
          <div 
            className="flex-1 h-44 border-2 border-dashed border-[#77C3FF] rounded-2xl bg-white/50 relative cursor-pointer hover:bg-white/70 transition-all group"
            onClick={handleStartMockInterview}
          >
            <div className="absolute inset-0 flex items-center justify-between p-6">
              <div className="flex-1">
                <div className="w-24 h-24 rounded-2xl overflow-hidden mb-4">
                              <img 
              src="/images/mock-interview.png" 
              alt="Mock Interview" 
              className="w-full h-full object-cover"
              onError={handleImageError}
            />
                </div>
                <h3 className="text-sm font-medium text-[#282828] text-center">Mock Interview</h3>
              </div>
              
              {/* Arrow Button */}
              <div className="w-12 h-12 rounded-full border-2 border-dashed border-[#68C6F1] bg-white/30 flex items-center justify-center group-hover:bg-white/60 transition-all">
                <svg className="w-5 h-5 text-[#68C6F1]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
                <svg className="w-5 h-5 text-[#68C6F1] -ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              </div>
            </div>
          </div>

          {/* Formal Interview Card */}
          <div 
            className="flex-1 h-44 border-2 border-dashed border-[#77C3FF] rounded-2xl bg-white/50 relative cursor-pointer hover:bg-white/70 transition-all group"
            onClick={handleStartFormalInterview}
          >
            <div className="absolute inset-0 flex items-center justify-between p-6">
              <div className="flex-1">
                <div className="w-24 h-24 rounded-2xl overflow-hidden mb-4">
                              <img 
              src="/images/formal-interview.png" 
              alt="Formal Interview" 
              className="w-full h-full object-cover"
              onError={handleImageError}
            />
                </div>
                <h3 className="text-sm font-medium text-[#282828] text-center">Formal Interview</h3>
              </div>
              
              {/* Arrow Button */}
              <div className="w-12 h-12 rounded-full border-2 border-dashed border-[#68C6F1] bg-white/30 flex items-center justify-center group-hover:bg-white/60 transition-all">
                <svg className="w-5 h-5 text-[#68C6F1]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
                <svg className="w-5 h-5 text-[#68C6F1] -ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              </div>
            </div>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex gap-4">
            <button
              onClick={() => setActiveTab('questions')}
              className={`px-6 py-3 rounded-lg font-medium transition-all ${
                activeTab === 'questions'
                  ? 'bg-white border border-[#68C6F1] text-[#3D3D3D] shadow-sm'
                  : 'bg-white text-[#3D3D3D] hover:border-[#68C6F1]'
              }`}
            >
              <div className="flex items-center">
                <svg className="w-5 h-5 text-[#68C6F1] mr-2" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6z"/>
                </svg>
                Question Bank
              </div>
            </button>
            <button
              onClick={() => setActiveTab('records')}
              className={`px-6 py-3 rounded-lg font-medium transition-all ${
                activeTab === 'records'
                  ? 'bg-white border border-[#68C6F1] text-[#3D3D3D] shadow-sm'
                  : 'bg-white text-[#3D3D3D] hover:border-[#68C6F1]'
              }`}
            >
              <div className="flex items-center">
                <svg className="w-5 h-5 text-[#68C6F1] mr-2" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M9 11H7v8h2v-8zm4-4h-2v12h2V7zm4-4h-2v16h2V3z"/>
                </svg>
                Interview Record
              </div>
            </button>
          </div>
          
          {/* Hidden Add button - commented out as requested */}
          {/* 
          <button
            className="px-6 py-3 bg-gradient-to-r from-[#9CFAFF] to-[#6BBAFF] text-white rounded-full font-medium hover:shadow-lg transition-all"
          >
            <div className="flex items-center">
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              Add
            </div>
          </button>
          */}
        </div>

        {/* Error Display */}
        {error && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
            <div className="text-red-600 text-sm">{error}</div>
          </div>
        )}

        {/* Tab Content */}
        {activeTab === 'questions' && (
          <div>
            {/* Question Bank Section */}
            <div className="mb-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-[#282828] font-medium">
                  Question Bank ({questionsWithAnswers.length})
                </h2>
                <button 
                  onClick={generateNewQuestions}
                  disabled={isGeneratingQuestions}
                  className={`px-4 py-2 rounded-lg text-sm transition-colors flex items-center gap-2 ${
                    isGeneratingQuestions 
                      ? 'bg-gray-300 text-gray-500 cursor-not-allowed' 
                      : 'bg-[#68C6F1] text-white hover:bg-[#5AB5E0]'
                  }`}
                >
                  {isGeneratingQuestions ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                      Generating...
                    </>
                  ) : (
                    <>
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                      </svg>
                      Generate New Questions
                    </>
                  )}
                </button>
              </div>
              
              <p className="text-[#282828] mb-6">
                This shows the questions and answers you've answered in interviews, which can be used for review and improvement.
              </p>

              {/* Questions Display */}
              <div className="space-y-6">
                {questionsLoading ? (
                  <div className="text-center py-8">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#68C6F1] mx-auto"></div>
                    <p className="text-[#666] mt-2">Loading questions...</p>
                  </div>
                ) : questionsError ? (
                  <div className="text-center py-8">
                    <p className="text-red-500 mb-4">{questionsError}</p>
                    <button 
                      onClick={loadQuestionsWithAnswers}
                      className="px-4 py-2 bg-[#68C6F1] text-white rounded-lg hover:bg-[#5AB5E0] transition-colors"
                    >
                      Retry
                    </button>
                  </div>
                ) : questionsWithAnswers.length > 0 ? (
                  questionsWithAnswers.map((question) => (
                    <div key={question.id} className="bg-white rounded-xl shadow-sm p-6">
                      <h3 className="text-lg font-semibold text-[#282828] mb-4">
                        {question.question_text}
                      </h3>
                      
                      {question.latest_answer ? (
                        <div className="text-sm text-[#666] leading-relaxed mb-4">
                          {question.latest_answer.answer_text.length > 300 
                            ? `${question.latest_answer.answer_text.substring(0, 300)}...`
                            : question.latest_answer.answer_text
                          }
                        </div>
                      ) : (
                        <div className="text-sm text-[#999] italic mb-4">
                          No answer yet - Click "Edit" to add your answer
                        </div>
                      )}
                      
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2 text-xs">
                          <span className={`px-2 py-1 rounded-full ${
                            question.question_type === 'technical' ? 'bg-blue-100 text-blue-800' :
                            question.question_type === 'behavioral' ? 'bg-green-100 text-green-800' :
                            question.question_type === 'situational' ? 'bg-purple-100 text-purple-800' :
                            'bg-gray-100 text-gray-800'
                          }`}>
                            {question.question_type}
                          </span>
                          <span className={`px-2 py-1 rounded-full ${
                            question.difficulty === 'easy' ? 'bg-green-100 text-green-800' :
                            question.difficulty === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-red-100 text-red-800'
                          }`}>
                            {question.difficulty}
                          </span>
                          {question.category && (
                            <span className="px-2 py-1 rounded-full bg-gray-100 text-gray-800">
                              {question.category}
                            </span>
                          )}
                          {question.latest_answer?.score && (
                            <span className="px-2 py-1 rounded-full bg-blue-100 text-blue-800">
                              Score: {Math.round(question.latest_answer.score)}
                            </span>
                          )}
                        </div>
                        
                        <div className="flex gap-2">
                          <button 
                            onClick={() => handleQuestionEdit(question.id)}
                            className="px-4 py-2 bg-white border border-gray-200 rounded-lg text-sm text-[#666] hover:border-[#68C6F1] transition-colors"
                            title="Edit question content and add your answer"
                          >
                            <div className="flex items-center">
                              <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 24 24">
                                <path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/>
                              </svg>
                              Edit
                            </div>
                          </button>
                          <button 
                            onClick={() => handleQuestionDelete(question.id)}
                            className="px-4 py-2 bg-white border border-gray-200 rounded-lg text-sm text-[#F16868] hover:border-red-300 transition-colors"
                          >
                            <div className="flex items-center">
                              <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 24 24">
                                <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
                              </svg>
                              Delete
                            </div>
                          </button>
                        </div>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-12">
                    <div className="w-16 h-16 bg-[#EEF9FF] rounded-xl mx-auto mb-4 flex items-center justify-center">
                      <svg className="w-8 h-8 text-[#68C6F1]" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6z"/>
                      </svg>
                    </div>
                    <p className="text-[#666] mb-4">No questions and answers yet</p>
                    <p className="text-[#999] text-sm mb-6">Start your first interview to build your question bank!</p>
                    <div className="flex gap-4 justify-center">
                      <button 
                        onClick={handleStartMockInterview}
                        className="px-6 py-2 bg-[#68C6F1] text-white rounded-lg hover:bg-[#5AB5E0] transition-colors"
                      >
                        Mock Interview
                      </button>
                      <button 
                        onClick={handleStartFormalInterview}
                        className="px-6 py-2 bg-[#34D399] text-white rounded-lg hover:bg-[#10B981] transition-colors"
                      >
                        Formal Interview
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'records' && (
          <div>
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-[#282828] font-semibold text-xl">
                Interview Record ({records.length})
              </h2>
              <button 
                onClick={refreshRecords}
                className="px-4 py-2 bg-[#68C6F1] text-white rounded-lg hover:bg-[#5AB5E0] transition-colors text-sm flex items-center gap-2"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                Refresh
              </button>
            </div>

            {/* Loading State */}
            {recordsLoading && (
              <div className="flex items-center justify-center py-12">
                <div className="text-center">
                  <div className="w-12 h-12 border-4 border-[#68C6F1] border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                  <p className="text-[#666]">Loading interview records...</p>
                </div>
              </div>
            )}

            {/* Error State */}
            {recordsError && !recordsLoading && (
              <div className="text-center py-12">
                <div className="w-16 h-16 bg-red-50 rounded-xl mx-auto mb-4 flex items-center justify-center">
                  <svg className="w-8 h-8 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <p className="text-red-600 mb-4">{recordsError}</p>
                <button 
                  onClick={refreshRecords}
                  className="px-6 py-2 bg-[#68C6F1] text-white rounded-lg hover:bg-[#5AB5E0] transition-colors"
                >
                  Retry
                </button>
              </div>
            )}

            {/* Records Table */}
            {!recordsLoading && !recordsError && (
              <div className="bg-white rounded-xl overflow-hidden">
                {records.length > 0 ? (
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead className="bg-[#F8FAFB] border-b border-[#E5E7EB]">
                        <tr>
                          <th className="px-6 py-4 text-left text-xs font-medium text-[#6B7280] uppercase tracking-wider">Interview ID</th>
                          <th className="px-6 py-4 text-left text-xs font-medium text-[#6B7280] uppercase tracking-wider">Date</th>
                          <th className="px-6 py-4 text-left text-xs font-medium text-[#6B7280] uppercase tracking-wider">Duration</th>
                          <th className="px-6 py-4 text-left text-xs font-medium text-[#6B7280] uppercase tracking-wider">Interview Type</th>
                          <th className="px-6 py-4 text-left text-xs font-medium text-[#6B7280] uppercase tracking-wider">Action</th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-[#E5E7EB]">
                        {records.map((record) => (
                          <tr key={record.id} className="hover:bg-[#F9FAFB] transition-colors">
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="flex items-center">
                                <div className="w-10 h-10 rounded-lg overflow-hidden mr-3 bg-[#EEF9FF] flex items-center justify-center">
                                  <img 
                                    src={record.type === 'Mock Interview' ? '/images/mock-interview.png' : '/images/formal-interview.png'}
                                    alt={record.type}
                                    className="w-8 h-8 object-contain"
                                    onError={(e) => {
                                      const target = e.target as HTMLImageElement;
                                      target.style.display = 'none';
                                      const parent = target.parentElement;
                                      if (parent) {
                                        parent.innerHTML = `
                                          <svg class="w-6 h-6 text-[#68C6F1]" fill="currentColor" viewBox="0 0 24 24">
                                            <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
                                          </svg>
                                        `;
                                      }
                                    }}
                                  />
                                </div>
                                <div>
                                  <div className="text-sm font-medium text-[#282828]">{record.title}</div>
                                  <div className="text-sm text-[#6B7280]">#{record.id}</div>
                                </div>
                              </div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-[#282828]">{record.date}</td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-[#282828]">{record.duration}</td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                                record.type === 'Mock Interview'
                                  ? 'bg-[#E8F5E8] text-[#2D7738]'
                                  : 'bg-[#EEF9FF] text-[#1B5E8C]'
                              }`}>
                                {record.type}
                              </span>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm">
                              <div className="flex items-center gap-2">
                                <button 
                                  onClick={() => handleReviewInterview(record)}
                                  className="px-4 py-2 bg-[#68C6F1] text-white rounded-lg hover:bg-[#5AB5E0] transition-colors text-xs font-medium"
                                >
                                  Review
                                </button>
                                <button 
                                  onClick={async () => {
                                    if (confirm('Are you sure you want to delete this interview record?')) {
                                      await deleteRecord(record.id);
                                    }
                                  }}
                                  className="px-4 py-2 bg-[#F87171] text-white rounded-lg hover:bg-[#EF4444] transition-colors text-xs font-medium"
                                >
                                  Delete
                                </button>
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <div className="w-16 h-16 bg-[#EEF9FF] rounded-xl mx-auto mb-4 flex items-center justify-center">
                      <svg className="w-8 h-8 text-[#68C6F1]" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M9 11H7v8h2v-8zm4-4h-2v12h2V7zm4-4h-2v16h2V3z"/>
                      </svg>
                    </div>
                    <p className="text-[#666] mb-4">No interview records yet</p>
                    <p className="text-[#999] text-sm mb-6">Start your first interview!</p>
                    <div className="flex gap-4 justify-center">
                      <button 
                        onClick={handleStartMockInterview}
                        className="px-6 py-2 bg-[#68C6F1] text-white rounded-lg hover:bg-[#5AB5E0] transition-colors"
                      >
                        Mock Interview
                      </button>
                      <button 
                        onClick={handleStartFormalInterview}
                        className="px-6 py-2 bg-[#34D399] text-white rounded-lg hover:bg-[#10B981] transition-colors"
                      >
                        Formal Interview
                      </button>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Floating User Info */}
      <div className="fixed bottom-6 right-6 z-50">
        <div className="bg-white rounded-2xl shadow-lg p-4 border border-gray-100">
          <div className="flex items-center space-x-3">
            {/* User Avatar */}
            <div className="w-12 h-12 rounded-full overflow-hidden bg-gradient-to-r from-[#9CFAFF] to-[#6BBAFF] flex items-center justify-center">
              {user?.avatar_url ? (
                <img 
                  src={user.avatar_url} 
                  alt={user.username || user.email}
                  className="w-full h-full object-cover"
                />
              ) : (
                <span className="text-white font-bold text-lg">
                  {user ? (user.username || user.email).charAt(0).toUpperCase() : 'U'}
                </span>
              )}
            </div>

            {/* User Information */}
            <div className="flex flex-col">
              <span className="text-sm font-semibold text-gray-900">
                {user?.username || user?.email || 'Guest'}
              </span>
              <span className="text-xs text-gray-500">
                {user ? user.email : 'Not logged in'}
              </span>
            </div>

            {/* Action Buttons */}
            <div className="flex flex-col gap-1">
              <button
                onClick={() => navigate('/profile')}
                className="px-3 py-1 text-xs bg-gray-100 hover:bg-gray-200 rounded-md transition-colors"
              >
                Settings
              </button>
              <button
                onClick={() => {
                  localStorage.removeItem('auth_token');
                  navigate('/login');
                }}
                className="px-3 py-1 text-xs text-red-600 hover:bg-red-50 rounded-md transition-colors"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Interview Detail Modal */}
      {showInterviewDetail && selectedInterviewRecord && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-4xl max-h-[80vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold text-gray-800">Interview Review</h2>
              <button 
                onClick={handleCloseInterviewDetail}
                className="text-gray-500 hover:text-gray-700"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            
            <div className="space-y-6">
              {/* Interview Overview */}
              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="text-lg font-semibold mb-3">Interview Overview</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <span className="text-sm text-gray-600">Title:</span>
                    <p className="font-medium">{selectedInterviewRecord.title}</p>
                  </div>
                  <div>
                    <span className="text-sm text-gray-600">Type:</span>
                    <p className="font-medium">{selectedInterviewRecord.type}</p>
                  </div>
                  <div>
                    <span className="text-sm text-gray-600">Date:</span>
                    <p className="font-medium">{selectedInterviewRecord.date}</p>
                  </div>
                  <div>
                    <span className="text-sm text-gray-600">Duration:</span>
                    <p className="font-medium">{selectedInterviewRecord.duration}</p>
                  </div>
                  <div>
                    <span className="text-sm text-gray-600">Status:</span>
                    <p className="font-medium">{selectedInterviewRecord.status}</p>
                  </div>
                  <div>
                    <span className="text-sm text-gray-600">Session ID:</span>
                    <p className="font-medium text-xs">{selectedInterviewRecord.session.session_id}</p>
                  </div>
                </div>
              </div>

              {/* Interview Statistics */}
              <div className="bg-blue-50 p-4 rounded-lg">
                <h3 className="text-lg font-semibold mb-3">Interview Statistics</h3>
                <div className="grid grid-cols-3 gap-4">
                  <div className="text-center">
                    <p className="text-2xl font-bold text-blue-600">{selectedInterviewRecord.session.total_questions}</p>
                    <p className="text-sm text-gray-600">Total Questions</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-green-600">{selectedInterviewRecord.session.completed_questions || 0}</p>
                    <p className="text-sm text-gray-600">Completed</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-orange-600">{selectedInterviewRecord.session.total_score || 'N/A'}</p>
                    <p className="text-sm text-gray-600">Score</p>
                  </div>
                </div>
              </div>

              {/* Interview Details */}
              <div className="bg-white border rounded-lg p-4">
                <h3 className="text-lg font-semibold mb-3">Interview Details</h3>
                <div className="space-y-2">
                  <p><span className="font-medium">Interview Type:</span> {selectedInterviewRecord.session.interview_type}</p>
                  <p><span className="font-medium">Started At:</span> {selectedInterviewRecord.session.started_at ? new Date(selectedInterviewRecord.session.started_at).toLocaleString() : 'Not started'}</p>
                  <p><span className="font-medium">Completed At:</span> {selectedInterviewRecord.session.completed_at ? new Date(selectedInterviewRecord.session.completed_at).toLocaleString() : 'Not completed'}</p>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex justify-end space-x-3">
                <button 
                  onClick={handleCloseInterviewDetail}
                  className="px-4 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 transition-colors"
                >
                  Close
                </button>
                <button 
                  onClick={handleViewFullDetails}
                  disabled={loadingFullDetails}
                  className="px-4 py-2 bg-[#68C6F1] text-white rounded-lg hover:bg-[#5AB5E0] transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center gap-2"
                >
                  {loadingFullDetails ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                      Loading...
                    </>
                  ) : (
                    'View Full Details'
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Full Interview Details Modal */}
      {showFullDetails && interviewFullData && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-6xl max-h-[90vh] overflow-y-auto w-full mx-4">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold text-gray-800">Complete Interview Review</h2>
              <button 
                onClick={() => setShowFullDetails(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            
            <div className="space-y-6">
              {/* Interview Summary */}
              <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-6 rounded-lg border border-blue-200">
                <h3 className="text-xl font-semibold mb-4 text-blue-800">Interview Summary</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="text-center">
                    <p className="text-3xl font-bold text-blue-600">{interviewFullData.total_questions}</p>
                    <p className="text-sm text-gray-600">Total Questions</p>
                  </div>
                  <div className="text-center">
                    <p className="text-3xl font-bold text-green-600">{interviewFullData.answers?.length || 0}</p>
                    <p className="text-sm text-gray-600">Answered</p>
                  </div>
                  <div className="text-center">
                    <p className="text-3xl font-bold text-orange-600">
                      {interviewFullData.answers?.length ? 
                        Math.round((interviewFullData.answers.reduce((sum: number, ans: any) => sum + (ans.score || 0), 0) / interviewFullData.answers.length)) 
                        : 'N/A'
                      }
                    </p>
                    <p className="text-sm text-gray-600">Avg Score</p>
                  </div>
                  <div className="text-center">
                    <p className="text-3xl font-bold text-purple-600">
                      {Math.round(((interviewFullData.answers?.length || 0) / interviewFullData.total_questions) * 100)}%
                    </p>
                    <p className="text-sm text-gray-600">Completion</p>
                  </div>
                </div>
              </div>

              {/* Questions and Answers */}
              <div className="space-y-4">
                <h3 className="text-xl font-semibold text-gray-800">Questions & Answers</h3>
                
                {interviewFullData.questions?.map((question: any, index: number) => {
                  const answer = interviewFullData.answers?.find((ans: any) => ans.question_id === question.id);
                  
                  return (
                    <div key={question.id} className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
                      {/* Question Header */}
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-2">
                            <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium">
                              Question {index + 1}
                            </span>
                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                              question.difficulty === 'easy' ? 'bg-green-100 text-green-800' :
                              question.difficulty === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                              'bg-red-100 text-red-800'
                            }`}>
                              {question.difficulty}
                            </span>
                            <span className="px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                              {question.question_type}
                            </span>
                          </div>
                          <h4 className="text-lg font-semibold text-gray-800 mb-2">
                            {question.question_text}
                          </h4>
                        </div>
                        {answer?.score && (
                          <div className="text-right">
                            <div className="text-2xl font-bold text-blue-600">{Math.round(answer.score)}</div>
                            <div className="text-xs text-gray-500">Score</div>
                          </div>
                        )}
                      </div>

                      {/* Answer Section */}
                      {answer ? (
                        <div className="space-y-4">
                          <div className="bg-gray-50 p-4 rounded-lg">
                            <h5 className="font-medium text-gray-700 mb-2">Your Answer:</h5>
                            <p className="text-gray-800 leading-relaxed">{answer.answer_text}</p>
                            <div className="flex items-center justify-between mt-3 text-sm text-gray-500">
                              <span>Answered at: {new Date(answer.answered_at).toLocaleString()}</span>
                              {answer.response_time && (
                                <span>Response time: {Math.round(answer.response_time)}s</span>
                              )}
                            </div>
                          </div>

                          {/* AI Feedback */}
                          {answer.ai_feedback && (
                            <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                              <h5 className="font-medium text-blue-800 mb-2">AI Feedback:</h5>
                              {answer.ai_feedback.strengths && (
                                <div className="mb-3">
                                  <p className="text-sm font-medium text-green-700 mb-1">Strengths:</p>
                                  <ul className="text-sm text-green-600 list-disc list-inside space-y-1">
                                    {answer.ai_feedback.strengths.map((strength: string, idx: number) => (
                                      <li key={idx}>{strength}</li>
                                    ))}
                                  </ul>
                                </div>
                              )}
                              {answer.ai_feedback.improvements && (
                                <div className="mb-3">
                                  <p className="text-sm font-medium text-orange-700 mb-1">Areas for Improvement:</p>
                                  <ul className="text-sm text-orange-600 list-disc list-inside space-y-1">
                                    {answer.ai_feedback.improvements.map((improvement: string, idx: number) => (
                                      <li key={idx}>{improvement}</li>
                                    ))}
                                  </ul>
                                </div>
                              )}
                              {answer.ai_feedback.suggestions && (
                                <div>
                                  <p className="text-sm font-medium text-blue-700 mb-1">Suggestions:</p>
                                  <ul className="text-sm text-blue-600 list-disc list-inside space-y-1">
                                    {answer.ai_feedback.suggestions.map((suggestion: string, idx: number) => (
                                      <li key={idx}>{suggestion}</li>
                                    ))}
                                  </ul>
                                </div>
                              )}
                            </div>
                          )}
                        </div>
                      ) : (
                        <div className="bg-gray-50 p-4 rounded-lg text-center">
                          <p className="text-gray-500 italic">This question was not answered</p>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>

              {/* Action Buttons */}
              <div className="flex justify-end space-x-3 pt-4 border-t">
                <button 
                  onClick={() => setShowFullDetails(false)}
                  className="px-6 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 transition-colors"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Job Selection Modal */}
      <JobSelectionModal
        isOpen={isJobModalOpen}
        onClose={handleJobModalClose}
        onConfirm={handleJobSelectionConfirm}
        availableJobs={jobs}
        interviewType={interviewType}
      />
    </div>
  );
};

export default HomePage; 