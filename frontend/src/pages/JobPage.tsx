import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { jobService, Job, JobTemplate, CreateJobData } from '../services/jobService';

const JobPage: React.FC = () => {
  const navigate = useNavigate();
  
  // State management
  const [selectedJobType, setSelectedJobType] = useState<string>('');
  const [jobTitle, setJobTitle] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  const [jobUrl, setJobUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');
  const [dragActive, setDragActive] = useState(false);

  // Preset job types
  const jobTypes = [
    'Product Manager',
    'Customer Service',
    'Marketing',
    'Accountant',
    'Sales Specialist',
    'Data Engineer',
    'User Operations',
    'Operations Manager'
  ];

  // Handle file drag
  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  };

  const handleFileUpload = async (file: File) => {
    // 检查文件类型
    const imageExtensions = ['png', 'jpg', 'jpeg', 'bmp', 'tiff', 'webp'];
    const fileExtension = file.name.split('.').pop()?.toLowerCase();
    
    if (imageExtensions.includes(fileExtension || '')) {
      // 处理图片文件 - OCR识别
      setLoading(true);
      setError('');
      
      try {
        console.log('开始OCR文字识别:', file.name);
        const result = await jobService.extractTextFromImage(file);
        
        if (result.text) {
          // 将识别的文本填充到Job description文本框
          setJobDescription(result.text);
          console.log('OCR识别成功，文本已填充到Job description');
        } else {
          setError('未能从图片中识别到文字内容');
        }
      } catch (err: any) {
        console.error('OCR识别失败:', err);
        setError(err.message || '图片文字识别失败，请重试');
      } finally {
        setLoading(false);
      }
    } else {
      // 其他文件类型的处理逻辑
      console.log('File uploaded:', file);
      setError('请上传图片文件（支持 PNG, JPG, JPEG, BMP, TIFF, WEBP 格式）');
    }
  };

  // Handle job type selection
  const handleJobTypeSelect = (jobType: string) => {
    setSelectedJobType(jobType);
    setJobTitle(jobType);
    setError(''); // Clear error message
  };

  // Handle job title input
  const handleJobTitleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setJobTitle(e.target.value);
    if (error) setError(''); // Clear error message
  };

  // Handle job description input
  const handleJobDescriptionChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setJobDescription(e.target.value);
    if (error) setError(''); // Clear error message
  };

  // Handle next step
  const handleNext = () => {
    if (!jobTitle.trim()) {
      setError('Please enter job title');
      return;
    }

    if (!jobDescription.trim()) {
      setError('Please enter job description');
      return;
    }

    navigate('/resume', {
      state: {
        jobTitle: jobTitle,
        jobDescription: jobDescription,
        selectedJobType: selectedJobType
      }
    });
  };

  // Handle return to home
  const handleHome = () => {
    navigate('/');
  };

  return (
    <div className="min-h-screen" style={{ backgroundColor: '#EEF9FF' }}>
      <div className="container mx-auto px-6 py-12 max-w-7xl">
        {/* Progress Steps */}
        <div className="flex items-center justify-center mb-12">
          <div className="bg-white rounded-full px-8 py-4 shadow-lg flex items-center space-x-16">
            {/* Job Step - Active */}
            <div className="flex items-center space-x-4">
              <div 
                className="w-9 h-9 rounded-full border-2 border-dashed flex items-center justify-center"
                style={{ 
                  backgroundColor: 'rgba(255, 255, 255, 0.3)',
                  borderColor: '#282828'
                }}
              >
                <svg className="w-4 h-4" style={{ color: '#282828' }} fill="currentColor" viewBox="0 0 16 16">
                  <path d="M8 2L6 4h4l-2-2zM4 6v8h8V6H4z"/>
                </svg>
              </div>
              <span 
                className="text-lg font-semibold"
                style={{ 
                  fontFamily: 'Poppins',
                  fontSize: '18px',
                  fontWeight: '600',
                  color: '#006FA2'
                }}
              >
                Job
              </span>
            </div>

            {/* Arrow */}
            <div 
              className="w-9 h-9 rounded-full border-2 border-dashed flex items-center justify-center"
              style={{ 
                backgroundColor: 'rgba(255, 255, 255, 0.3)',
                borderColor: '#282828'
              }}
            >
              <svg className="w-4 h-4" style={{ color: '#282828' }} fill="currentColor" viewBox="0 0 16 16">
                <path d="M6 4l4 4-4 4V4z"/>
              </svg>
            </div>

            {/* Resume Step */}
            <div className="flex items-center space-x-4">
              <div 
                className="w-9 h-9 rounded-full border-2 border-dashed flex items-center justify-center"
                style={{ 
                  backgroundColor: 'rgba(255, 255, 255, 0.3)',
                  borderColor: '#282828'
                }}
              >
                <svg className="w-4 h-4" style={{ color: '#282828' }} fill="currentColor" viewBox="0 0 16 16">
                  <path d="M6 4l4 4-4 4V4z"/>
                </svg>
              </div>
              <span 
                className="text-lg"
                style={{ 
                  fontFamily: 'Poppins',
                  fontSize: '18px',
                  fontWeight: '400',
                  color: '#282828'
                }}
              >
                Resume
              </span>
            </div>

            {/* Arrow */}
            <div 
              className="w-9 h-9 rounded-full border-2 border-dashed flex items-center justify-center"
              style={{ 
                backgroundColor: 'rgba(255, 255, 255, 0.3)',
                borderColor: '#282828'
              }}
            >
              <svg className="w-4 h-4" style={{ color: '#282828' }} fill="currentColor" viewBox="0 0 16 16">
                <path d="M6 4l4 4-4 4V4z"/>
              </svg>
            </div>

            {/* Complete Step */}
            <div className="flex items-center space-x-4">
              <div 
                className="w-9 h-9 rounded-full border-2 border-dashed flex items-center justify-center"
                style={{ 
                  backgroundColor: 'rgba(255, 255, 255, 0.3)',
                  borderColor: '#282828'
                }}
              >
                <svg className="w-4 h-4" style={{ color: '#282828' }} fill="currentColor" viewBox="0 0 16 16">
                  <path d="M6 4l4 4-4 4V4z"/>
                </svg>
              </div>
              <span 
                className="text-lg"
                style={{ 
                  fontFamily: 'Poppins',
                  fontSize: '18px',
                  fontWeight: '400',
                  color: '#282828'
                }}
              >
                Complete
              </span>
            </div>
          </div>
        </div>

        {/* Main Title */}
        <div className="text-center mb-8">
          <h1 
            className="mb-4"
            style={{
              fontFamily: 'Poppins',
              fontSize: '23px',
              fontWeight: '500',
              lineHeight: '127.07%',
              color: '#262626'
            }}
          >
            Which job interview are you preparing for?
          </h1>
          <p 
            style={{
              fontFamily: 'Poppins',
              fontSize: '15px',
              fontWeight: '400',
              lineHeight: '141%',
              color: '#666666'
            }}
          >
            Customized interview questions and answers based on your position
          </p>
        </div>

        {/* Main Content Area */}
        <div className="flex gap-8 mb-8">
          {/* Left Side - Job Selection */}
          <div className="w-64">
            {/* Your Job Placeholder */}
            <div 
              className="w-48 h-13 rounded-xl border border-dashed mb-8 flex items-center justify-center cursor-pointer"
              style={{
                backgroundColor: '#FFFFFF',
                borderColor: '#68C6F1',
                borderRadius: '12px'
              }}
            >
              <span 
                style={{
                  fontFamily: 'Poppins',
                  fontSize: '18px',
                  fontWeight: '400',
                  color: '#282828'
                }}
              >
                Your Job
              </span>
            </div>

            {/* Examples Divider */}
            <div className="relative mb-6">
              <div 
                className="absolute inset-0 flex items-center"
                style={{ top: '11px' }}
              >
                <div 
                  className="w-full border-t"
                  style={{ 
                    borderColor: 'rgba(0, 110, 200, 0.22)',
                    borderStyle: 'dashed'
                  }}
                />
              </div>
              <div className="relative flex justify-center">
                <span 
                  className="bg-white px-4"
                  style={{
                    fontFamily: 'Poppins',
                    fontSize: '16px',
                    fontWeight: '400',
                    lineHeight: '141%',
                    color: '#004B6D'
                  }}
                >
                  Examples
                </span>
              </div>
            </div>

            {/* Job Type Options */}
            <div className="space-y-3">
              {jobTypes.map((jobType, index) => (
                <div
                  key={index}
                  onClick={() => handleJobTypeSelect(jobType)}
                  className={`w-48 h-13 rounded-xl cursor-pointer flex items-center justify-center transition-colors ${
                    selectedJobType === jobType ? 'ring-2 ring-blue-500' : ''
                  }`}
                  style={{
                    backgroundColor: '#FFFFFF',
                    borderRadius: '12px'
                  }}
                >
                  <span 
                    style={{
                      fontFamily: 'Poppins',
                      fontSize: '15px',
                      fontWeight: '400',
                      color: '#282828'
                    }}
                  >
                    {jobType}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Right Side - Upload and Input Areas */}
          <div className="flex-1">
            <div className="flex gap-4 mb-6">
              {/* File Upload Area */}
              <div 
                className={`flex-1 h-37 rounded-2xl border border-dashed flex flex-col items-center justify-center cursor-pointer relative ${
                  loading ? 'opacity-50 pointer-events-none' : ''
                }`}
                style={{
                  backgroundColor: 'rgba(255, 255, 255, 0.6)',
                  borderColor: '#77C3FF',
                  borderRadius: '16px'
                }}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
              >
                {loading ? (
                  <div className="flex flex-col items-center">
                    <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mb-3"></div>
                    <p 
                      className="text-center"
                      style={{
                        fontFamily: 'Poppins',
                        fontSize: '14px',
                        fontWeight: '400',
                        color: '#666666'
                      }}
                    >
                      正在识别图片中的文字...
                    </p>
                  </div>
                ) : (
                  <>
                    {/* Upload Icon */}
                    <div className="mb-4">
                  <div className="relative">
                    {/* Background rectangles */}
                    <div 
                      className="absolute w-8 h-6 rounded"
                      style={{
                        backgroundColor: '#E4EEFF',
                        top: '1px',
                        left: '10px'
                      }}
                    />
                    <div 
                      className="absolute w-10 h-8 rounded"
                      style={{
                        backgroundColor: '#C3D8FF',
                        top: '5px',
                        left: '5px'
                      }}
                    />
                    <div 
                      className="w-12 h-10 rounded-md relative"
                      style={{
                        backgroundColor: '#75A6FF',
                        borderRadius: '5px'
                      }}
                    >
                      {/* Plus icon */}
                      <div 
                        className="absolute w-5 h-5 rounded-full flex items-center justify-center"
                        style={{
                          backgroundColor: '#2F51FF',
                          right: '-10px',
                          bottom: '-10px'
                        }}
                      >
                        <svg className="w-2.5 h-2.5" style={{ color: '#FFFFFF' }} fill="currentColor" viewBox="0 0 10 10">
                          <path d="M8.75 3.75H6.25V1.25C6.25 0.5625 5.6875 0 5 0C4.3125 0 3.75 0.5625 3.75 1.25V3.75H1.25C0.5625 3.75 0 4.3125 0 5C0 5.6875 0.5625 6.25 1.25 6.25H3.75V8.75C3.75 9.4375 4.3125 10 5 10C5.6875 10 6.25 9.4375 6.25 8.75V6.25H8.75C9.4375 6.25 10 5.6875 10 5C10 4.3125 9.4375 3.75 8.75 3.75Z"/>
                        </svg>
                      </div>
                    </div>
                  </div>
                </div>
                <p 
                  className="text-center mb-2"
                  style={{
                    fontFamily: 'Poppins',
                    fontSize: '15px',
                    fontWeight: '400',
                    color: '#282828',
                    maxWidth: '291px'
                  }}
                >
                  Drag and drop or upload a screenshot of the job description
                </p>
                <p 
                  className="text-center text-xs"
                  style={{
                    fontFamily: 'Poppins',
                    fontSize: '12px',
                    fontWeight: '400',
                    color: '#666666',
                    maxWidth: '291px'
                  }}
                >
                  支持图片格式: PNG, JPG, JPEG, BMP, TIFF, WEBP
                </p>
                <input
                  type="file"
                  accept="image/*"
                  onChange={(e) => {
                    if (e.target.files && e.target.files[0]) {
                      handleFileUpload(e.target.files[0]);
                    }
                  }}
                  className="hidden"
                  id="image-upload"
                />
                <label
                  htmlFor="image-upload"
                  className="mt-3 px-4 py-2 rounded-lg cursor-pointer transition-colors text-sm"
                  style={{ 
                    background: 'linear-gradient(181deg, #9CFAFF 0%, #A3E4FF 19%, #6BBAFF 95%)',
                    color: '#383838',
                    fontFamily: 'Poppins'
                  }}
                >
                  选择图片文件
                </label>
                  </>
                )}
              </div>

              {/* URL Input Area */}
              <div 
                className="w-96 h-37 rounded-2xl border border-dashed flex flex-col items-center justify-center"
                style={{
                  backgroundColor: 'rgba(255, 255, 255, 0.6)',
                  borderColor: '#77C3FF',
                  borderRadius: '16px'
                }}
              >
                <div className="flex items-center mb-2">
                  <div 
                    className="w-12 h-10 rounded-lg flex items-center justify-center mr-2"
                    style={{
                      backgroundColor: '#E4F5FF',
                      borderRadius: '8px'
                    }}
                  >
                    <svg className="w-7 h-7" style={{ color: '#75A6FF' }} fill="currentColor" viewBox="0 0 24 24">
                      <path d="M12.232 4.232a2.5 2.5 0 013.536 3.536l-1.225 1.224a.75.75 0 001.061 1.061l1.224-1.224a4 4 0 00-5.657-5.657l-3 3a4 4 0 00.225 5.865.75.75 0 00.977-1.138 2.5 2.5 0 01-.142-3.667l3-3z"/>
                      <path d="M11.768 19.768a2.5 2.5 0 01-3.536-3.536l1.225-1.224a.75.75 0 00-1.061-1.061l-1.224 1.224a4 4 0 005.657 5.657l3-3a4 4 0 00-.225-5.865.75.75 0 00-.977 1.138 2.5 2.5 0 01.142 3.667l-3 3z"/>
                    </svg>
                  </div>
                  <div 
                    className="px-3 py-2 rounded-lg"
                    style={{
                      backgroundColor: '#75A6FF',
                      borderRadius: '8px'
                    }}
                  >
                    <span 
                      style={{
                        fontFamily: 'Poppins',
                        fontSize: '12px',
                        fontWeight: '500',
                        lineHeight: '141%',
                        color: '#FFFFFF'
                      }}
                    >
                      Analyze
                    </span>
                  </div>
                  <div className="w-12 text-center">
                    <span 
                      style={{
                        fontFamily: 'Poppins',
                        fontSize: '12px',
                        color: '#666666'
                      }}
                    >
                      Either
                    </span>
                  </div>
                </div>
                <p 
                  className="text-center mb-1"
                  style={{
                    fontFamily: 'Poppins',
                    fontSize: '15px',
                    fontWeight: '400',
                    color: '#282828'
                  }}
                >
                  Paste the job link,
                </p>
                <p 
                  className="text-center text-xs"
                  style={{
                    fontFamily: 'Poppins',
                    fontSize: '12px',
                    fontWeight: '400',
                    color: '#666666'
                  }}
                >
                  e.g. https://www.example.com/jobs?id=abc123
                </p>
              </div>
            </div>

            {/* Job Title Input */}
            <div 
              className="w-full h-17 rounded-xl mb-4 relative"
              style={{
                backgroundColor: '#FFFFFF',
                borderRadius: '12px',
                boxShadow: '0px 2px 8px 0px rgba(145, 215, 255, 0.2)'
              }}
            >
              <div className="p-6">
                <label 
                  className="block mb-2"
                  style={{
                    fontFamily: 'Poppins',
                    fontSize: '16px',
                    fontWeight: '400',
                    lineHeight: '141%',
                    color: '#333333'
                  }}
                >
                  Job title
                </label>
                <input
                  type="text"
                  value={jobTitle}
                  onChange={handleJobTitleChange}
                  placeholder="Please enter the job title..."
                  className="w-full border-none outline-none bg-transparent"
                  style={{
                    fontFamily: 'Poppins',
                    fontSize: '14px',
                    color: '#333333'
                  }}
                  maxLength={50}
                />
                <div 
                  className="absolute bottom-6 right-6 text-xs"
                  style={{
                    fontFamily: 'Poppins',
                    fontSize: '12px',
                    color: '#666666'
                  }}
                >
                  {jobTitle.length}/50
                </div>
              </div>
            </div>

            {/* Job Description Input */}
            <div 
              className="w-full rounded-xl relative"
              style={{
                backgroundColor: '#FFFFFF',
                borderRadius: '12px',
                boxShadow: '0px 2px 8px 0px rgba(145, 215, 255, 0.2)',
                height: '335px'
              }}
            >
              <div className="p-6 h-full flex flex-col">
                <label 
                  className="block mb-2"
                  style={{
                    fontFamily: 'Poppins',
                    fontSize: '16px',
                    fontWeight: '400',
                    lineHeight: '141%',
                    color: '#333333'
                  }}
                >
                  Job description
                </label>
                <p 
                  className="text-xs mb-4"
                  style={{
                    fontFamily: 'Poppins',
                    fontSize: '12px',
                    fontWeight: '400',
                    color: '#999999'
                  }}
                >
                  Copy and paste the job description here. We will generate customized questions and answers through the big model to help you improve your interview performance
                </p>
                <textarea
                  value={jobDescription}
                  onChange={handleJobDescriptionChange}
                  placeholder="Please enter the job description..."
                  className="flex-1 border border-gray-200 rounded-lg p-3 outline-none resize-none focus:border-blue-400 focus:ring-1 focus:ring-blue-400"
                  style={{
                    fontFamily: 'Poppins',
                    fontSize: '14px',
                    color: '#333333',
                    backgroundColor: '#FAFAFA'
                  }}
                  maxLength={2000}
                />
                <div 
                  className="text-right text-xs mt-2"
                  style={{
                    fontFamily: 'Poppins',
                    fontSize: '12px',
                    color: '#666666'
                  }}
                >
                  {jobDescription.length}/2000
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <span className="text-red-700">{error}</span>
          </div>
        )}

        {/* Bottom Navigation */}
        <div className="flex justify-center space-x-6">
          {/* Home Button */}
          <button
            onClick={handleHome}
            className="flex items-center space-x-2 px-8 py-3 rounded-full transition-all duration-200"
            style={{
              backgroundColor: '#FFFFFF',
              boxShadow: '0px 2px 8px 0px rgba(145, 215, 255, 0.2)',
              opacity: 0.9
            }}
          >
            <svg className="w-5 h-5" style={{ color: '#363636' }} fill="currentColor" viewBox="0 0 20 20">
              <path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z"/>
            </svg>
            <span 
              style={{
                fontFamily: 'Poppins',
                fontSize: '20px',
                fontWeight: '400',
                color: '#363636'
              }}
            >
              Home
            </span>
          </button>

          {/* Next Button */}
          <button
            onClick={handleNext}
            disabled={!jobTitle.trim() || !jobDescription.trim()}
            className="flex items-center space-x-2 px-8 py-3 rounded-full transition-all duration-200 disabled:opacity-50"
            style={{
              background: 'linear-gradient(181deg, #9CFAFF 0%, #A3E4FF 19%, #6BBAFF 95%)',
              boxShadow: '0px 2px 8px 0px rgba(145, 215, 255, 0.2)'
            }}
          >
            <span 
              style={{
                fontFamily: 'Poppins',
                fontSize: '20px',
                fontWeight: '400',
                color: '#383838'
              }}
            >
              Next
            </span>
            <svg className="w-5 h-5" style={{ color: '#383838' }} fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd"/>
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
};

export default JobPage; 