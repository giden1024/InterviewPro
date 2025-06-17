import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

const CompletePage: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { 
    jobTitle, 
    jobDescription, 
    resumeText, 
    experienceLevel, 
    uploadedFile 
  } = location.state || {};

  const handleStartInterview = () => {
    // 这里可以跳转到面试练习页面
    navigate('/interview', {
      state: {
        jobTitle,
        jobDescription,
        resumeText,
        experienceLevel,
        uploadedFile
      }
    });
  };

  const handleHome = () => {
    navigate('/');
  };

  return (
    <div className="min-h-screen bg-blue-50 py-12">
      <div className="container mx-auto px-6 max-w-4xl">
        {/* Progress Steps */}
        <div className="flex items-center justify-center mb-12">
          <div className="bg-white rounded-full px-8 py-4 shadow-lg flex items-center space-x-16">
            {/* Job Step - Completed */}
            <div className="flex items-center space-x-4">
              <div className="w-9 h-9 bg-green-100 border-2 border-green-500 rounded-full flex items-center justify-center">
                <svg className="w-4 h-4 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd"/>
                </svg>
              </div>
              <span className="text-green-600 text-lg">Job</span>
            </div>

            {/* Arrow */}
            <div className="w-9 h-9 bg-green-100 border-2 border-green-500 rounded-full flex items-center justify-center">
              <svg className="w-4 h-4 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd"/>
              </svg>
            </div>

            {/* Resume Step - Completed */}
            <div className="flex items-center space-x-4">
              <div className="w-9 h-9 bg-green-100 border-2 border-green-500 rounded-full flex items-center justify-center">
                <svg className="w-4 h-4 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd"/>
                </svg>
              </div>
              <span className="text-green-600 text-lg">Resume</span>
            </div>

            {/* Arrow */}
            <div className="w-9 h-9 bg-green-100 border-2 border-green-500 rounded-full flex items-center justify-center">
              <svg className="w-4 h-4 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd"/>
              </svg>
            </div>

            {/* Complete Step - Current */}
            <div className="flex items-center space-x-4">
              <div className="w-9 h-9 bg-blue-100 border-2 border-blue-500 rounded-full flex items-center justify-center">
                <svg className="w-4 h-4 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
              </div>
              <span className="text-blue-800 text-lg font-semibold">Complete</span>
            </div>
          </div>
        </div>

        {/* Success Content */}
        <div className="text-center mb-12">
          {/* Success Icon */}
          <div className="flex justify-center mb-6">
            <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center">
              <svg className="w-12 h-12 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd"/>
              </svg>
            </div>
          </div>

          <h1 className="text-3xl font-bold text-gray-800 mb-4">
            Setup Complete!
          </h1>
          <p className="text-lg text-gray-600 mb-8">
            Great! We've got everything we need to generate personalized interview questions for you.
          </p>
        </div>

        {/* Summary */}
        <div className="bg-white rounded-xl shadow-sm p-8 mb-8">
          <h2 className="text-xl font-semibold text-gray-800 mb-6">Your Interview Setup</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Job Information */}
            <div className="bg-blue-50 rounded-lg p-4">
              <h3 className="font-medium text-blue-800 mb-2">Position</h3>
              <p className="text-gray-700">{jobTitle || 'Not specified'}</p>
              {experienceLevel && (
                <div className="mt-2">
                  <span className="inline-block bg-blue-200 text-blue-800 text-xs px-2 py-1 rounded">
                    {experienceLevel}
                  </span>
                </div>
              )}
            </div>

            {/* Resume Information */}
            <div className="bg-green-50 rounded-lg p-4">
              <h3 className="font-medium text-green-800 mb-2">Resume</h3>
              {uploadedFile ? (
                <p className="text-gray-700">File: {uploadedFile}</p>
              ) : resumeText ? (
                <p className="text-gray-700">Text resume uploaded</p>
              ) : (
                <p className="text-gray-500">No resume provided</p>
              )}
            </div>
          </div>

          {/* Job Description Preview */}
          {jobDescription && (
            <div className="mt-6 bg-gray-50 rounded-lg p-4">
              <h3 className="font-medium text-gray-800 mb-2">Job Description</h3>
              <p className="text-gray-600 text-sm line-clamp-3">{jobDescription}</p>
            </div>
          )}
        </div>

        {/* Action Buttons */}
        <div className="flex justify-center space-x-6">
          {/* Home Button */}
          <button
            onClick={handleHome}
            className="bg-white text-gray-700 px-8 py-3 rounded-full font-medium text-lg transition-all duration-200 shadow-md hover:shadow-lg flex items-center space-x-2"
          >
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z"/>
            </svg>
            <span>Home</span>
          </button>

          {/* Start Interview Button */}
          <button
            onClick={handleStartInterview}
            className="bg-gradient-to-r from-green-400 to-green-600 hover:from-green-500 hover:to-green-700 text-white px-8 py-3 rounded-full font-medium text-lg transition-all duration-200 shadow-lg hover:shadow-xl flex items-center space-x-2"
          >
            <span>Start Interview Practice</span>
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clipRule="evenodd"/>
            </svg>
          </button>
        </div>

        {/* Additional Info */}
        <div className="text-center mt-8">
          <p className="text-gray-500 text-sm">
            We'll generate customized questions based on your job requirements and experience level.
          </p>
        </div>
      </div>
    </div>
  );
};

export default CompletePage; 