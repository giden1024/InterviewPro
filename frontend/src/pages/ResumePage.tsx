import React, { useState, useCallback } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

const ResumePage: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { jobTitle, jobDescription } = location.state || {};
  
  const [resumeText, setResumeText] = useState<string>('');
  const [selectedLevel, setSelectedLevel] = useState<string>('Interns');
  const [dragActive, setDragActive] = useState(false);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);

  const experienceLevels = ['Interns', 'Graduate', 'Junior', 'Senior'];

  const handleBack = () => {
    navigate('/job');
  };

  const handleNext = () => {
    if (resumeText.trim() || uploadedFile) {
      // 进入Complete页面，传递所有数据
      navigate('/complete', { 
        state: { 
          jobTitle, 
          jobDescription,
          resumeText,
          experienceLevel: selectedLevel,
          uploadedFile: uploadedFile?.name 
        } 
      });
    }
  };

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
      if (file.type === 'application/pdf' || 
          file.type === 'application/msword' || 
          file.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document') {
        setUploadedFile(file);
        // 这里可以添加文件读取逻辑
        console.log('Uploaded file:', file.name);
      } else {
        alert('Please upload a PDF or Word document');
      }
    }
  }, []);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setUploadedFile(file);
      console.log('Selected file:', file.name);
    }
  };

  return (
    <div className="min-h-screen bg-blue-50 py-12">
      <div className="container mx-auto px-6 max-w-6xl">
        {/* Progress Steps */}
        <div className="flex items-center justify-center mb-12">
          <div className="bg-white rounded-full px-8 py-4 shadow-lg flex items-center space-x-16">
            {/* Job Step - Completed */}
            <div className="flex items-center space-x-4">
              <div className="w-9 h-9 bg-gray-100 bg-opacity-50 border-2 border-gray-800 border-dashed rounded-full flex items-center justify-center backdrop-blur-sm shadow-lg">
                <svg className="w-4 h-4 text-gray-800" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M8 5l5 5-5 5V5z"/>
                </svg>
              </div>
              <span className="text-gray-600 text-lg">Job</span>
            </div>

            {/* Arrow */}
            <div className="w-9 h-9 bg-gray-100 bg-opacity-50 border-2 border-gray-800 border-dashed rounded-full flex items-center justify-center backdrop-blur-sm shadow-lg">
              <svg className="w-4 h-4 text-gray-800" fill="currentColor" viewBox="0 0 20 20">
                <path d="M8 5l5 5-5 5V5z"/>
              </svg>
            </div>

            {/* Resume Step - Current */}
            <div className="flex items-center space-x-4">
              <div className="w-9 h-9 bg-blue-100 border-2 border-blue-500 rounded-full flex items-center justify-center">
                <svg className="w-4 h-4 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M8 5l5 5-5 5V5z"/>
                </svg>
              </div>
              <span className="text-blue-800 text-lg font-semibold">Resume</span>
            </div>

            {/* Arrow */}
            <div className="w-9 h-9 bg-gray-50 bg-opacity-60 border-2 border-gray-400 border-dashed rounded-full flex items-center justify-center backdrop-blur-sm shadow-md">
              <svg className="w-4 h-4 text-gray-500" fill="currentColor" viewBox="0 0 20 20">
                <path d="M8 5l5 5-5 5V5z"/>
              </svg>
            </div>

            {/* Complete Step */}
            <div className="flex items-center space-x-4">
              <div className="w-9 h-9 bg-gray-50 bg-opacity-60 border-2 border-gray-400 border-dashed rounded-full flex items-center justify-center backdrop-blur-sm shadow-md">
                <svg className="w-4 h-4 text-gray-500" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
              </div>
              <span className="text-gray-400 text-lg">Complete</span>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="text-center mb-8">
          <h1 className="text-2xl font-medium text-gray-800 mb-4">
            Please upload your resume
          </h1>
          <p className="text-gray-600">
            We want to get to know you and generate custom interview questions for you
          </p>
        </div>

        {/* Upload Area */}
        <div 
          className={`mb-6 border-2 border-dashed rounded-2xl p-16 text-center transition-colors ${
            dragActive 
              ? 'border-blue-400 bg-blue-50' 
              : 'border-blue-300 bg-white bg-opacity-60'
          }`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          {/* Upload Icon */}
          <div className="flex justify-center mb-6 relative">
            <div className="w-12 h-12 relative">
              {/* Document Icon */}
              <svg className="w-12 h-12 text-blue-600" fill="currentColor" viewBox="0 0 24 24">
                <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z"/>
                <path d="M8,12H16V14H8V12M8,16H13V18H8V16Z"/>
              </svg>
              {/* Plus Icon */}
              <div className="absolute -bottom-1 -right-1 w-5 h-5 bg-blue-600 rounded-full flex items-center justify-center">
                <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M10 3v14M3 10h14" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                </svg>
              </div>
            </div>
          </div>

          {uploadedFile ? (
            <div className="space-y-2">
              <p className="text-green-600 font-medium">File uploaded: {uploadedFile.name}</p>
              <p className="text-gray-500 text-sm">Click to select a different file</p>
            </div>
          ) : (
            <div className="space-y-2">
              <p className="text-gray-800 font-medium">
                Drag and drop resume here to upload
              </p>
              <p className="text-gray-500 text-sm">
                Or click to select a file to upload（PDF or Word Document）
              </p>
            </div>
          )}

          {/* Hidden File Input */}
          <input
            type="file"
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            accept=".pdf,.doc,.docx"
            onChange={handleFileSelect}
          />
        </div>

        {/* Resume Text Area */}
        <div className="bg-white rounded-xl p-6 shadow-sm mb-6">
          <p className="text-xs text-gray-500 mb-4">
            You can also paste your resume text directly here, but we recommend uploading your resume file
          </p>
          <textarea
            value={resumeText}
            onChange={(e) => setResumeText(e.target.value)}
            className="w-full h-80 border-none outline-none resize-none text-gray-800 placeholder-gray-400"
            placeholder="Paste your resume text here..."
            maxLength={3000}
          />
          <div className="text-right mt-2">
            <span className="text-xs text-gray-500">{resumeText.length}/3000</span>
          </div>
        </div>

        {/* Experience Level Selection */}
        <div className="mb-12">
          <div className="flex justify-center space-x-4">
            {experienceLevels.map((level) => (
              <button
                key={level}
                onClick={() => setSelectedLevel(level)}
                className={`px-6 py-2 rounded-lg text-sm font-medium transition-all ${
                  selectedLevel === level
                    ? 'bg-gradient-to-r from-blue-400 to-blue-600 text-white shadow-lg'
                    : 'bg-blue-100 text-gray-700 hover:bg-blue-200'
                }`}
              >
                {level}
              </button>
            ))}
          </div>
        </div>

        {/* Bottom Navigation */}
        <div className="flex justify-center space-x-6">
          {/* Back Button */}
          <button
            onClick={handleBack}
            className="bg-white text-gray-700 px-8 py-3 rounded-full font-medium text-lg transition-all duration-200 shadow-md hover:shadow-lg flex items-center space-x-2"
          >
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clipRule="evenodd"/>
            </svg>
            <span>Back</span>
          </button>

          {/* Next Button */}
          <button
            onClick={handleNext}
            disabled={!resumeText.trim() && !uploadedFile}
            className={`px-8 py-3 rounded-full font-medium text-lg transition-all duration-200 shadow-lg flex items-center space-x-2 ${
              (resumeText.trim() || uploadedFile)
                ? 'bg-gradient-to-r from-blue-400 to-blue-600 hover:from-blue-500 hover:to-blue-700 text-white hover:shadow-xl'
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }`}
          >
            <span>Next</span>
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd"/>
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
};

export default ResumePage; 