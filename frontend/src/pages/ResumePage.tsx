import React, { useState, useCallback, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { resumeService, Resume } from '../services/resumeService';
import { jobService } from '../services/jobService';
import { questionService } from '../services/questionService';
import { interviewService } from '../services/interviewService';
import { useUserInfo } from '../hooks/useUserInfo';
import { useAuthRedirect } from '../hooks/useAuthRedirect';

interface LocationState {
  jobTitle?: string;
  jobDescription?: string;
  jobId?: string;
  company?: string;
  requirements?: string[];
  skills?: string[];
}

interface ResumeAnalysis {
  match_score?: number;
  overall_score?: number;
  suggestions?: string[];
  analysis?: any;
  score?: number;
}

const ResumePage: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { user } = useUserInfo();
  const { handleApiError } = useAuthRedirect();
  const { jobTitle, jobDescription, jobId, company } = (location.state as LocationState) || {};
  
  // State management
  const [resumeText, setResumeText] = useState<string>('');
  const [selectedLevel, setSelectedLevel] = useState<string>('Interns');
  const [dragActive, setDragActive] = useState(false);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [selectedResume, setSelectedResume] = useState<Resume | null>(null);
  const [analysis, setAnalysis] = useState<ResumeAnalysis | null>(null);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState<string>('');
  const [saving, setSaving] = useState(false);
  const [generating, setGenerating] = useState(false);

  const experienceLevels = ['Interns', 'Graduate', 'Junior', 'Senior'];

  // Load user's resume list when page loads
  useEffect(() => {
    loadUserResumes();
  }, []);

  // Load user resume list
  const loadUserResumes = async () => {
    try {
      setLoading(true);
      const response = await resumeService.getResumes();
      setResumes(response.resumes || []);
    } catch (err) {
      console.error('Failed to load resume list:', err);
      handleApiError(err);
      setError('Failed to load resume list');
    } finally {
      setLoading(false);
    }
  };

  // File upload handling
  const handleFileUpload = async (file: File) => {
    if (!file) return;

    // Validate file type
    const allowedTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
    if (!allowedTypes.includes(file.type)) {
      setError('Please upload PDF or Word document');
      return;
    }

    // Validate file size (10MB)
    if (file.size > 10 * 1024 * 1024) {
      setError('File size cannot exceed 10MB');
      return;
    }

    try {
      setUploading(true);
      setError('');
      
      const resume = await resumeService.uploadResume(file);
      
      // Check if returned resume object is valid
      if (!resume || !resume.id) {
        console.error('Invalid resume object:', resume);
        setError('Upload successful but resume data is invalid, please refresh and try again');
        return;
      }
      
      setUploadedFile(file);
      setSelectedResume(resume);
      
      // Auto analyze resume
      await analyzeResume(resume.id);
      
      // Update resume list
      await loadUserResumes();
      
    } catch (err) {
      console.error('Failed to upload resume:', err);
      handleApiError(err);
      setError(`Failed to upload resume: ${err instanceof Error ? err.message : 'Please try again later'}`);
    } finally {
      setUploading(false);
    }
  };

  // Analyze resume
  const analyzeResume = async (resumeId: number) => {
    try {
      setAnalyzing(true);
      const analysisResult = await resumeService.analyzeResume(resumeId, {
        include_suggestions: true,
        include_score: true
      });
      
      // 提取实际的分析数据
      const analysisData = (analysisResult as any).analysis || (analysisResult as any).data || analysisResult;
      console.log('Analysis result:', analysisResult);
      console.log('Setting analysis data:', analysisData);
      setAnalysis(analysisData);
    } catch (err) {
      console.error('Failed to analyze resume:', err);
      setError('Failed to analyze resume');
    } finally {
      setAnalyzing(false);
    }
  };

  // Drag handling
  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      handleFileUpload(file);
    }
  }, []);

  // File selection handling
  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFileUpload(e.target.files[0]);
    }
  };

  // Text resume handling
  const handleTextResume = async () => {
    if (!resumeText.trim()) {
      setError('Please enter resume content');
      return null;
    }

    try {
      setUploading(true);
      setError('');
      
      // Create temporary file and upload
      const blob = new Blob([resumeText], { type: 'text/plain' });
      const file = new File([blob], `resume_${Date.now()}.txt`, { type: 'text/plain' });
      
      const resume = await resumeService.uploadResume(file);
      
      setSelectedResume(resume);
      await analyzeResume(resume.id);
      await loadUserResumes();
      
      return resume; // Return created resume
      
    } catch (err) {
      console.error('Failed to create text resume:', err);
      setError('Failed to create resume, please try again later');
      return null;
    } finally {
      setUploading(false);
    }
  };

  const handleBack = () => {
    navigate('/jobs');
  };

  const handleNext = async () => {
    if (!selectedResume && !resumeText.trim() && !uploadedFile) {
      setError('Please upload resume or enter resume content first');
      return;
    }

    try {
      setSaving(true);
      setError('');

      // 1. Ensure resume ID exists
      let currentResumeId = selectedResume?.id;
      if (!currentResumeId && resumeText.trim()) {
        // If only text, create resume first
        const createdResume = await handleTextResume();
        if (!createdResume) {
          setError('Unable to create resume, please retry');
          return;
        }
        currentResumeId = createdResume.id;
      }

      if (!currentResumeId) {
        setError('Unable to get resume information, please retry');
        return;
      }

      // 2. Save job record (if job information exists)
      let savedJobId = jobId;
      if (jobTitle && !jobId) {
        try {
          const jobData = {
            title: jobTitle,
            company: company || '',
            description: jobDescription || '',
            resume_id: currentResumeId, // ✅ 关键修复：添加简历关联
            requirements: [],
            responsibilities: [],
            experience_level: selectedLevel,
            job_type: 'full-time' as const,
            skills_required: []
          };
          
          const savedJob = await jobService.createJob(jobData);
          savedJobId = savedJob.id.toString();
          console.log('Job saved successfully:', savedJob);
        } catch (jobError) {
          console.error('Failed to save job record:', jobError);
          // Don't block the process, continue execution
        }
      }

      // 3. Navigate to Complete page, pass data but don't create interview session
      navigate('/complete', { 
        state: { 
          jobTitle, 
          jobDescription,
          jobId: savedJobId,
          company,
          resumeId: currentResumeId,
          resumeText,
          experienceLevel: selectedLevel,
          completed: false,
          questionsGenerated: false
        } 
      });

    } catch (error) {
      console.error('Processing failed:', error);
      setError(error instanceof Error ? error.message : 'Processing failed, please retry');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="min-h-screen" style={{ backgroundColor: '#EEF9FF' }}>
      <div className="container mx-auto px-6 max-w-5xl py-12">
        {/* Progress Steps - Based on design mockup */}
        <div className="flex items-center justify-center mb-8">
          <div 
            className="rounded-full px-8 py-4 flex items-center space-x-16"
            style={{ 
              backgroundColor: '#FFFFFF',
              boxShadow: '0px 0px 20px 0px rgba(156, 250, 255, 0.3)'
            }}
          >
            {/* Job Step */}
            <div className="flex items-center space-x-4">
              <div 
                className="w-9 h-9 rounded-full flex items-center justify-center"
                style={{ 
                  backgroundColor: 'rgba(255, 255, 255, 0.3)',
                  border: '2px dashed #282828',
                  backdropFilter: 'blur(3.94px)',
                  boxShadow: '0px 1.31px 3.94px 0px rgba(0, 0, 0, 0.03)'
                }}
              >
                <svg className="w-4 h-4" style={{ color: '#282828' }} fill="currentColor" viewBox="0 0 20 20">
                  <path d="M8 5l5 5-5 5V5z"/>
                </svg>
              </div>
              <span className="text-lg" style={{ color: '#282828', fontFamily: 'Poppins', fontWeight: 400 }}>Job</span>
            </div>

            {/* Arrow */}
            <div 
              className="w-9 h-9 rounded-full flex items-center justify-center"
              style={{ 
                backgroundColor: 'rgba(255, 255, 255, 0.3)',
                border: '2px dashed #282828',
                backdropFilter: 'blur(3.94px)',
                boxShadow: '0px 1.31px 3.94px 0px rgba(0, 0, 0, 0.03)'
              }}
            >
              <svg className="w-4 h-4" style={{ color: '#282828' }} fill="currentColor" viewBox="0 0 20 20">
                <path d="M8 5l5 5-5 5V5z"/>
              </svg>
            </div>

            {/* Resume Step - Active */}
            <div className="flex items-center space-x-4">
              <div 
                className="w-9 h-9 rounded-full flex items-center justify-center"
                style={{ 
                  backgroundColor: 'rgba(255, 255, 255, 0.3)',
                  border: '2px dashed #282828',
                  backdropFilter: 'blur(3.94px)',
                  boxShadow: '0px 1.31px 3.94px 0px rgba(0, 0, 0, 0.03)'
                }}
              >
                <svg className="w-4 h-4" style={{ color: '#282828' }} fill="currentColor" viewBox="0 0 20 20">
                  <path d="M8 5l5 5-5 5V5z"/>
                </svg>
              </div>
              <span className="text-lg font-semibold" style={{ color: '#006FA2', fontFamily: 'Poppins', fontWeight: 600 }}>Resume</span>
            </div>

            {/* Arrow */}
            <div 
              className="w-9 h-9 rounded-full flex items-center justify-center"
              style={{ 
                backgroundColor: 'rgba(255, 255, 255, 0.3)',
                border: '2px dashed #282828',
                backdropFilter: 'blur(3.94px)',
                boxShadow: '0px 1.31px 3.94px 0px rgba(0, 0, 0, 0.03)'
              }}
            >
              <svg className="w-4 h-4" style={{ color: '#282828' }} fill="currentColor" viewBox="0 0 20 20">
                <path d="M8 5l5 5-5 5V5z"/>
              </svg>
            </div>

            {/* Complete Step */}
            <div className="flex items-center space-x-4">
              <div 
                className="w-9 h-9 rounded-full flex items-center justify-center"
                style={{ 
                  backgroundColor: 'rgba(255, 255, 255, 0.3)',
                  border: '2px dashed #282828',
                  backdropFilter: 'blur(3.94px)',
                  boxShadow: '0px 1.31px 3.94px 0px rgba(0, 0, 0, 0.03)'
                }}
              >
                <svg className="w-4 h-4" style={{ color: '#282828' }} fill="currentColor" viewBox="0 0 20 20">
                  <path d="M8 5l5 5-5 5V5z"/>
                </svg>
              </div>
              <span className="text-lg" style={{ color: '#282828', fontFamily: 'Poppins', fontWeight: 400 }}>Complete</span>
            </div>
          </div>
        </div>

        {/* Title and Description */}
        <div className="text-center mb-8">
          <h1 
            className="text-2xl font-medium mb-4"
            style={{ 
              color: '#262626', 
              fontFamily: 'Poppins',
              fontSize: '23px',
              lineHeight: '127.06%'
            }}
          >
            Please upload your resume
          </h1>
          <p 
            className="text-base"
            style={{ 
              color: '#666666', 
              fontFamily: 'Poppins',
              fontSize: '15px',
              lineHeight: '141%'
            }}
          >
            We want to get to know you and generate custom interview questions for you
          </p>
        </div>

        {/* Error Display */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <div className="text-red-600 text-sm">{error}</div>
          </div>
        )}

        {/* File Upload Area */}
        <div className="mb-6">
          <div 
            className={`border-2 border-dashed rounded-2xl p-12 text-center transition-colors ${
              dragActive 
                ? 'border-blue-400 bg-blue-50' 
                : ''
            }`}
            style={{ 
              borderColor: '#77C3FF',
              backgroundColor: 'rgba(255, 255, 255, 0.6)'
            }}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            {uploading ? (
              <div className="space-y-4">
                <div className="w-16 h-16 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
                <p style={{ color: '#666666' }}>Uploading and parsing resume...</p>
              </div>
            ) : uploadedFile ? (
              <div className="space-y-4">
                <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto">
                  <svg className="w-8 h-8 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                </div>
                <p className="text-green-600 font-medium">✅ {uploadedFile.name}</p>
                <p style={{ color: '#666666' }} className="text-sm">File uploaded successfully</p>
              </div>
            ) : (
              <div className="space-y-4">
                {/* File Icon */}
                <div className="w-12 h-12 mx-auto relative">
                  <div 
                    className="w-10 h-12 rounded-sm"
                    style={{ backgroundColor: '#75A6FF' }}
                  >
                    {/* File corner */}
                    <div 
                      className="absolute top-0 right-0 w-2.5 h-2.5"
                      style={{ backgroundColor: '#75A6FF' }}
                    />
                    {/* File content lines */}
                    <div className="p-2 space-y-1">
                      <div className="h-0.5 bg-white w-6"></div>
                      <div className="h-0.5 bg-white w-4"></div>
                    </div>
                  </div>
                  {/* Plus icon */}
                  <div 
                    className="absolute -bottom-1 -right-1 w-5 h-5 rounded-full flex items-center justify-center"
                    style={{ backgroundColor: '#2F51FF' }}
                  >
                    <svg className="w-2.5 h-2.5 text-white" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clipRule="evenodd" />
                    </svg>
                  </div>
                </div>

                <div>
                  <p 
                    className="text-lg font-medium mb-2"
                    style={{ color: '#282828', fontFamily: 'Poppins', fontSize: '15px' }}
                  >
                    Drag and drop resume here to upload
                  </p>
                  <p 
                    className="text-sm mb-4"
                    style={{ color: '#666666', fontFamily: 'Poppins', fontSize: '12px' }}
                  >
                    Or click to select a file to upload（PDF or Word Document）
                  </p>
                  <input
                    type="file"
                    accept=".pdf,.doc,.docx"
                    onChange={handleFileSelect}
                    className="hidden"
                    id="resume-upload"
                  />
                  <label
                    htmlFor="resume-upload"
                    className="inline-block px-6 py-3 rounded-lg cursor-pointer transition-colors"
                    style={{ 
                      background: 'linear-gradient(181deg, #9CFAFF 0%, #A3E4FF 19%, #6BBAFF 95%)',
                      color: '#383838'
                    }}
                  >
                                          Select File
                  </label>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Text Input Area */}
        <div className="mb-8">
          <div 
            className="rounded-xl p-6"
            style={{ 
              backgroundColor: '#FFFFFF',
              boxShadow: '0px 2px 8px 0px rgba(145, 215, 255, 0.2)'
            }}
          >
            <p 
              className="text-sm mb-4"
              style={{ color: '#999999', fontFamily: 'Poppins', fontSize: '12px' }}
            >
              You can also paste your resume text directly here, but we recommend uploading your resume file
            </p>
            <textarea
              value={resumeText}
              onChange={(e) => setResumeText(e.target.value)}
                              placeholder="Please paste your resume content..."
              className="w-full h-64 p-4 border-0 resize-none focus:outline-none"
              style={{ backgroundColor: 'transparent' }}
            />
            <div className="flex justify-between items-center mt-4">
              <span 
                className="text-sm"
                style={{ color: '#666666', fontFamily: 'Poppins', fontSize: '12px' }}
              >
                {resumeText.length}/3000
              </span>

            </div>
          </div>
        </div>

        {/* Experience Level Tags */}
        <div className="mb-8">
          <div className="flex justify-center space-x-3">
            {experienceLevels.map((level) => (
              <button
                key={level}
                onClick={() => setSelectedLevel(level)}
                className={`px-6 py-2 rounded-lg transition-colors ${
                  selectedLevel === level
                    ? 'text-gray-700'
                    : 'text-gray-700'
                }`}
                style={{ 
                  background: selectedLevel === level ? 'linear-gradient(181deg, #9CFAFF 0%, #A3E4FF 19%, #6BBAFF 95%)' : '#E4F5FF',
                  fontFamily: 'Poppins',
                  fontSize: '15px',
                  lineHeight: '141%'
                }}
              >
                {level}
              </button>
            ))}
          </div>
        </div>

        {/* Navigation Buttons */}
        <div className="flex justify-center space-x-6">
          {/* Back Button */}
          <button
            onClick={handleBack}
            className="px-12 py-3 rounded-full transition-colors flex items-center space-x-2"
            style={{ 
              backgroundColor: '#FFFFFF',
              color: '#363636',
              opacity: 0.9
            }}
          >
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M9.707 16.707a1 1 0 01-1.414 0l-6-6a1 1 0 010-1.414l6-6a1 1 0 011.414 1.414L5.414 9H17a1 1 0 110 2H5.414l4.293 4.293a1 1 0 010 1.414z" clipRule="evenodd" />
            </svg>
            <span style={{ fontFamily: 'Poppins', fontSize: '20px' }}>Back</span>
          </button>

          {/* Next Button */}
          <button
            onClick={handleNext}
            disabled={(!selectedResume && !resumeText.trim() && !uploadedFile) || saving || generating}
            className="px-12 py-3 rounded-full transition-colors flex items-center space-x-2 disabled:opacity-50"
            style={{ 
              background: 'linear-gradient(181deg, #9CFAFF 0%, #A3E4FF 19%, #6BBAFF 95%)',
              color: '#383838'
            }}
          >
            {saving || generating ? (
              <>
                <div className="w-5 h-5 border-2 border-gray-600 border-t-transparent rounded-full animate-spin"></div>
                <span style={{ fontFamily: 'Poppins', fontSize: '20px' }}>
                  {saving && !generating ? 'Saving...' : generating ? 'Generating questions...' : 'Processing...'}
                </span>
              </>
            ) : (
              <>
                <span style={{ fontFamily: 'Poppins', fontSize: '20px' }}>Next</span>
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
              </>
            )}
          </button>
        </div>

        {/* Resume Analysis - Show if analysis results exist */}
        {analysis && (
          <div className="mt-8 bg-white rounded-xl shadow-sm p-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">Resume Analysis Results</h3>
            
            {analyzing ? (
              <div className="text-center py-8">
                <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                <p className="text-gray-600">Analyzing resume...</p>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-blue-50 p-4 rounded-lg">
                    <div className="text-2xl font-bold text-blue-600">{analysis.match_score || analysis.score || 0}%</div>
                    <div className="text-sm text-gray-600">Score</div>
                  </div>
                  <div className="bg-green-50 p-4 rounded-lg">
                    <div className="text-2xl font-bold text-green-600">{analysis.overall_score || analysis.score || 0}%</div>
                    <div className="text-sm text-gray-600">Overall Score</div>
                  </div>
                </div>


              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default ResumePage; 