import React from 'react';
import { useNavigate } from 'react-router-dom';

const LandingPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-[#EEF9FF]">
      {/* Navigation Bar */}
      <nav className="flex items-center justify-between px-8 py-4 bg-white shadow-sm">
        <div className="flex items-center">
          <div className="w-10 h-10 bg-gradient-to-r from-[#9CFAFF] to-[#6BBAFF] rounded-full flex items-center justify-center mr-3">
            <span className="text-white font-bold text-lg">O</span>
          </div>
          <span className="text-xl font-bold text-[#282828]">Offerotter</span>
        </div>
        <div className="flex items-center space-x-4">
          <button
            onClick={() => navigate('/login')}
            className="px-4 py-2 text-[#282828] hover:text-[#68C6F1] transition-colors"
          >
            Login
          </button>
          <button
            onClick={() => navigate('/register')}
            className="px-4 py-2 text-[#68C6F1] border border-[#68C6F1] rounded-full hover:bg-[#68C6F1] hover:text-white transition-all"
          >
            Sign Up
          </button>
          <button
            onClick={() => navigate('/home')}
            className="px-6 py-2 bg-gradient-to-r from-[#9CFAFF] to-[#6BBAFF] text-white rounded-full hover:shadow-lg transition-all"
          >
            Get Started
          </button>
        </div>
      </nav>

      {/* Main Content */}
      <div className="flex">
        {/* Left Column */}
        <div className="w-1/3 p-8">
          {/* Hero Section */}
          <div className="mb-12">
            <h1 className="text-4xl font-bold text-[#282828] mb-6">
              Master Your<br />
              <span className="text-[#68C6F1]">Interview Skills</span>
            </h1>
            <p className="text-lg text-[#3D3D3D] mb-8 leading-relaxed">
              Practice with AI-powered mock interviews, get personalized feedback, 
              and land your dream job with confidence.
            </p>
            <button
              onClick={() => navigate('/home')}
              className="px-8 py-4 bg-gradient-to-r from-[#9CFAFF] to-[#6BBAFF] text-white rounded-xl text-lg font-semibold shadow-lg hover:shadow-xl transform hover:scale-105 transition-all"
            >
              Start Practicing Now
            </button>
          </div>

          {/* Features */}
          <div className="space-y-6">
            <div className="flex items-center p-4 bg-white rounded-xl shadow-sm">
              <div className="w-12 h-12 bg-[#E4EEFF] rounded-lg flex items-center justify-center mr-4">
                <svg className="w-6 h-6 text-[#68C6F1]" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                </svg>
              </div>
              <div>
                <h3 className="font-semibold text-[#282828]">AI-Powered Practice</h3>
                <p className="text-sm text-[#3D3D3D]">Realistic interview scenarios</p>
              </div>
            </div>

            <div className="flex items-center p-4 bg-white rounded-xl shadow-sm">
              <div className="w-12 h-12 bg-[#E4EEFF] rounded-lg flex items-center justify-center mr-4">
                <svg className="w-6 h-6 text-[#68C6F1]" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
              </div>
              <div>
                <h3 className="font-semibold text-[#282828]">Instant Feedback</h3>
                <p className="text-sm text-[#3D3D3D]">Get detailed performance analysis</p>
              </div>
            </div>

            <div className="flex items-center p-4 bg-white rounded-xl shadow-sm">
              <div className="w-12 h-12 bg-[#E4EEFF] rounded-lg flex items-center justify-center mr-4">
                <svg className="w-6 h-6 text-[#68C6F1]" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M13 10V3L4 14h7v7l9-11h-7z"/>
                </svg>
              </div>
              <div>
                <h3 className="font-semibold text-[#282828]">Track Progress</h3>
                <p className="text-sm text-[#3D3D3D]">Monitor your improvement over time</p>
              </div>
            </div>
          </div>
        </div>

        {/* Middle Column */}
        <div className="w-1/3 p-8">
          <div className="bg-white rounded-2xl shadow-lg p-8 h-full">
            <div className="text-center mb-8">
              <div className="w-24 h-24 bg-gradient-to-r from-[#9CFAFF] to-[#6BBAFF] rounded-full mx-auto mb-4 flex items-center justify-center">
                <svg className="w-12 h-12 text-white" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                </svg>
              </div>
              <h2 className="text-2xl font-bold text-[#282828] mb-2">Ready to Practice?</h2>
              <p className="text-[#3D3D3D]">Join thousands of successful candidates</p>
            </div>

            <div className="space-y-4">
              <button
                onClick={() => navigate('/jobs')}
                className="w-full p-4 bg-[#EEF9FF] border-2 border-dashed border-[#77C3FF] rounded-xl text-center hover:bg-[#E4EEFF] transition-colors"
              >
                <div className="text-lg font-semibold text-[#282828] mb-1">Choose Your Role</div>
                <div className="text-sm text-[#3D3D3D]">Select from 100+ job positions</div>
              </button>

              <button
                onClick={() => navigate('/resume')}
                className="w-full p-4 bg-[#EEF9FF] border-2 border-dashed border-[#77C3FF] rounded-xl text-center hover:bg-[#E4EEFF] transition-colors"
              >
                <div className="text-lg font-semibold text-[#282828] mb-1">Upload Resume</div>
                <div className="text-sm text-[#3D3D3D]">Get personalized questions</div>
              </button>

              <button
                onClick={() => navigate('/interview')}
                className="w-full p-4 bg-gradient-to-r from-[#9CFAFF] to-[#6BBAFF] text-white rounded-xl text-center hover:shadow-lg transition-all"
              >
                <div className="text-lg font-semibold mb-1">Start Mock Interview</div>
                <div className="text-sm opacity-90">Begin your practice session</div>
              </button>
            </div>
          </div>
        </div>

        {/* Right Column */}
        <div className="w-1/3 p-8">
          <div className="bg-white rounded-2xl shadow-lg p-6 mb-6">
            <h3 className="text-xl font-bold text-[#282828] mb-4">Success Stories</h3>
            <div className="space-y-4">
              <div className="flex items-start">
                <div className="w-10 h-10 bg-[#68C6F1] rounded-full flex items-center justify-center mr-3">
                  <span className="text-white font-bold text-sm">JS</span>
                </div>
                <div>
                  <p className="text-sm text-[#3D3D3D] mb-1">
                    "Offerotter helped me land my dream job at Google! The mock interviews were incredibly realistic."
                  </p>
                  <p className="text-xs text-[#68C6F1] font-semibold">- Jessica Smith, Software Engineer</p>
                </div>
              </div>

              <div className="flex items-start">
                <div className="w-10 h-10 bg-[#87D2F6] rounded-full flex items-center justify-center mr-3">
                  <span className="text-white font-bold text-sm">MJ</span>
                </div>
                <div>
                  <p className="text-sm text-[#3D3D3D] mb-1">
                    "The AI feedback was spot-on and helped me improve my communication skills significantly."
                  </p>
                  <p className="text-xs text-[#68C6F1] font-semibold">- Michael Johnson, Product Manager</p>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-gradient-to-br from-[#E4EEFF] to-[#EEF9FF] rounded-2xl p-6">
            <h3 className="text-lg font-bold text-[#282828] mb-3">Statistics</h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-[#68C6F1]">98%</div>
                <div className="text-xs text-[#3D3D3D]">Success Rate</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-[#68C6F1]">10K+</div>
                <div className="text-xs text-[#3D3D3D]">Users</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-[#68C6F1]">50K+</div>
                <div className="text-xs text-[#3D3D3D]">Interviews</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-[#68C6F1]">4.9/5</div>
                <div className="text-xs text-[#3D3D3D]">Rating</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LandingPage; 