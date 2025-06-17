import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUserInfo } from '../hooks/useUserInfo';

const HomePage: React.FC = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('questions');
  const { user, isLoading, error, fetchUserInfo } = useUserInfo();

  useEffect(() => {
    // 页面加载时获取用户信息
    fetchUserInfo();
  }, []);

  return (
    <div className="min-h-screen bg-[#EEF9FF] flex">
      {/* Left Sidebar */}
      <div className="w-60 bg-white shadow-lg">
        {/* Logo */}
        <div className="p-6 border-b">
          <div className="flex items-center">
            <div className="w-10 h-10 bg-gradient-to-r from-[#9CFAFF] to-[#6BBAFF] rounded-full flex items-center justify-center mr-3">
              <span className="text-white font-bold text-lg">O</span>
            </div>
            <span className="text-xl font-bold text-[#282828]">Offerotter</span>
          </div>
        </div>

        {/* Add New Jobs Card */}
        <div className="p-4">
          <div className="border-2 border-dashed border-[#77C3FF] rounded-2xl p-6 text-center bg-[#EEF9FF]">
            <div className="w-12 h-12 bg-gradient-to-r from-[#9CFAFF] to-[#6BBAFF] rounded-xl mx-auto mb-3 flex items-center justify-center">
              <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 4v16m8-8H4"/>
              </svg>
            </div>
            <h3 className="font-medium text-[#282828] text-sm">Add New Jobs</h3>
          </div>
        </div>

        {/* Jobs List */}
        <div className="px-4 pb-4">
          <h3 className="text-[#282828] font-medium mb-3">Jobs</h3>
          <div className="space-y-2">
            <div className="p-3 bg-white border border-[#68C6F1] rounded-xl cursor-pointer hover:shadow-md transition-all">
              <span className="text-[#282828] text-sm">Product Manager</span>
            </div>
            <div className="p-3 bg-white border border-transparent rounded-xl cursor-pointer hover:border-[#68C6F1] transition-all">
              <span className="text-[#282828] text-sm">Marketing Planner</span>
            </div>
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
                {isLoading ? '加载中...' : (user?.username || user?.email || 'Guest')}
              </div>
              <div className="text-xs text-[#333333]">
                {user ? `ID:${user.id}` : 'Not logged in'}
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
            View Profile
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 p-6">
        {/* Header placeholders */}
        <div className="flex gap-6 mb-6">
          <div className="flex-1 h-44 bg-white border-2 border-dashed border-[#77C3FF] rounded-2xl flex items-center justify-center">
            <div className="text-center text-[#282828]">
              <div className="w-16 h-16 bg-[#EEF9FF] rounded-xl mx-auto mb-2 flex items-center justify-center">
                <svg className="w-8 h-8 text-[#68C6F1]" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
                </svg>
              </div>
              <span className="text-sm">Feature Placeholder</span>
            </div>
          </div>
          <div className="flex-1 h-44 bg-white border-2 border-dashed border-[#77C3FF] rounded-2xl flex items-center justify-center">
            <div className="text-center text-[#282828]">
              <div className="w-16 h-16 bg-[#EEF9FF] rounded-xl mx-auto mb-2 flex items-center justify-center">
                <svg className="w-8 h-8 text-[#68C6F1]" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M9 11H7v8h2v-8zm4-4h-2v12h2V7zm4-4h-2v16h2V3z"/>
                </svg>
              </div>
              <span className="text-sm">Analytics Placeholder</span>
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
          
          <button
            onClick={() => navigate('/interview')}
            className="px-6 py-3 bg-gradient-to-r from-[#9CFAFF] to-[#6BBAFF] text-white rounded-full font-medium hover:shadow-lg transition-all"
          >
            <div className="flex items-center">
              <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 4v16m8-8H4"/>
              </svg>
              Add
            </div>
          </button>
        </div>

        {/* Interview Questions Header */}
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-[#282828] font-medium">Interview questions（2/10）</h2>
          <button className="p-2 bg-white rounded-lg shadow-sm hover:shadow-md transition-all">
            <div className="flex items-center gap-2">
              <svg className="w-5 h-5 text-[#68C6F1]" fill="currentColor" viewBox="0 0 24 24">
                <path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/>
              </svg>
              <svg className="w-5 h-5 text-[#F16868]" fill="currentColor" viewBox="0 0 24 24">
                <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
              </svg>
            </div>
          </button>
        </div>

        {/* Description */}
        <p className="text-[#282828] mb-6">
          Conduct a mock interview to get more customized questions ! (we generate 2 questions based on your resume）
        </p>

        {/* Question Sections */}
        <div className="space-y-6">
          {/* Question 1 */}
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-start justify-between mb-4">
              <h3 className="text-lg font-semibold text-[#282828] flex-1">
                How would you design a campaign to recruit new live streamers in a market where live streaming is still stigmatized?​​
              </h3>
              <button className="ml-4 p-2 bg-white rounded-lg shadow-sm hover:shadow-md transition-all">
                <div className="flex items-center gap-2">
                  <svg className="w-5 h-5 text-[#68C6F1]" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/>
                  </svg>
                  <svg className="w-5 h-5 text-[#F16868]" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
                  </svg>
                </div>
              </button>
            </div>
            <p className="text-[#282828] text-sm leading-relaxed">
              To tackle stigma, I'd focus on reframing live streaming as a tool for ​​community empowerment​​ rather than just entertainment. For example, in Indonesia, I'd partner with local religious leaders or educators to launch a campaign like 'Knowledge Live,' where respected figures (e.g., Quran teachers, traditional artisans) demonstrate how streaming helps them share skills or preserve culture. To incentivize participation, I'd create a 'First Stream Kit'—offering free lighting filters and halal-compliant............
            </p>
          </div>

          {/* Question 2 */}
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-start justify-between mb-4">
              <h3 className="text-lg font-semibold text-[#282828] flex-1">
                How would you measure the success of a live streamer recruitment campaign?​​
              </h3>
              <button className="ml-4 p-2 bg-white rounded-lg shadow-sm hover:shadow-md transition-all">
                <div className="flex items-center gap-2">
                  <svg className="w-5 h-5 text-[#68C6F1]" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/>
                  </svg>
                  <svg className="w-5 h-5 text-[#F16868]" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
                  </svg>
                </div>
              </button>
            </div>
            <p className="text-[#282828] text-sm leading-relaxed">
              Quality of adoption​​: % of new streamers who complete ≥3 streams (measuring retention, not just interest).Sentiment shift​​: Pre/post-campaign surveys on perceptions (e.g., 'Is streaming a respectable career?').Efficiency​​: Cost-per-engaged-streamer (CPES), factoring in training/resources provided.For example, if we recruit 1,000 streamers but only 200 stay active after a month, I'd investigate pain points (e.g., monetization clarity) and iterate. I'd also benchmark against local competitors' retention rates to contextualize results.
            </p>
          </div>

          {/* Interview Options */}
          <div className="flex gap-6 mt-8">
            <div className="flex-1">
              <div className="bg-white rounded-2xl p-6 text-center hover:shadow-lg transition-all cursor-pointer" onClick={() => navigate('/interview')}>
                <div className="w-24 h-24 bg-[#EEF9FF] rounded-2xl mx-auto mb-4 flex items-center justify-center">
                  <div className="w-16 h-16 bg-[#68C6F1] rounded-xl flex items-center justify-center">
                    <svg className="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M8 5v14l11-7z"/>
                    </svg>
                  </div>
                </div>
                <h3 className="font-medium text-[#282828] mb-2">Mock Interview</h3>
                <div className="flex items-center justify-center">
                  <div className="w-12 h-12 bg-gray-100 rounded-full border-2 border-dashed border-[#68C6F1] flex items-center justify-center">
                    <svg className="w-6 h-6 text-[#68C6F1]" fill="currentColor" viewBox="0 0 24 24">
                      <path d="m8.5 8.5-1 1 5 5 1-1-5-5z"/>
                      <path d="m13.5 8.5-5 5 1 1 5-5-1-1z"/>
                    </svg>
                  </div>
                </div>
              </div>
            </div>

            <div className="flex-1">
              <div className="bg-white rounded-2xl p-6 text-center hover:shadow-lg transition-all cursor-pointer">
                <div className="w-24 h-24 bg-[#EEF9FF] rounded-2xl mx-auto mb-4 flex items-center justify-center">
                  <div className="w-16 h-16 bg-[#87D2F6] rounded-xl flex items-center justify-center">
                    <svg className="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                    </svg>
                  </div>
                </div>
                <h3 className="font-medium text-[#282828] mb-2">Formal Interview</h3>
                <div className="flex items-center justify-center">
                  <div className="w-12 h-12 bg-gray-100 rounded-full border-2 border-dashed border-[#68C6F1] flex items-center justify-center">
                    <svg className="w-6 h-6 text-[#68C6F1]" fill="currentColor" viewBox="0 0 24 24">
                      <path d="m8.5 8.5-1 1 5 5 1-1-5-5z"/>
                      <path d="m13.5 8.5-5 5 1 1 5-5-1-1z"/>
                    </svg>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 右下角用户信息 */}
      <div className="fixed bottom-6 right-6 z-50">
        <div className="bg-white rounded-2xl shadow-lg p-4 border border-gray-100">
          <div className="flex items-center space-x-3">
            {/* 用户头像 */}
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

            {/* 用户信息 */}
            <div className="flex flex-col">
              <span className="text-sm font-semibold text-gray-900">
                {isLoading ? '加载中...' : (user?.username || user?.email || 'Guest')}
              </span>
              <span className="text-xs text-gray-500">
                {user ? user.email : 'Not logged in'}
              </span>
            </div>

            {/* 操作按钮 */}
            <div className="flex flex-col space-y-1">
              <button
                onClick={() => navigate('/profile')}
                className="p-2 text-gray-600 hover:text-[#68C6F1] hover:bg-gray-50 rounded-lg transition-colors"
                title="查看个人资料"
              >
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
                </svg>
              </button>
              {error && (
                <button
                  onClick={fetchUserInfo}
                  className="p-2 text-red-500 hover:text-red-700 hover:bg-red-50 rounded-lg transition-colors"
                  title="重新获取用户信息"
                >
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M17.65 6.35C16.2 4.9 14.21 4 12 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08c-.82 2.33-3.04 4-5.65 4-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z"/>
                  </svg>
                </button>
              )}
            </div>
          </div>
          
          {error && (
            <div className="mt-2 text-xs text-red-500 bg-red-50 p-2 rounded-lg">
              {error}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default HomePage; 