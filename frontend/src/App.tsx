import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LandingPage from './pages/LandingPage';
import LandingPage1 from './pages/LandingPage1';
import HomePage from './pages/HomePage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import ResumePage from './pages/ResumePage';
import JobPage from './pages/JobPage';
import CompletePage from './pages/CompletePage';
import MockInterviewPage from './pages/MockInterviewPage';
import FormalInterviewPage from './pages/FormalInterviewPage';
import { InterviewRecordPage } from './pages/InterviewRecordPage';
import UserProfilePage from './pages/UserProfilePage';
import PrivacyPolicyPage from './pages/PrivacyPolicyPage';
import TermsOfUsePage from './pages/TermsOfUsePage';
import OAuthCallbackPage from './pages/OAuthCallbackPage';
import { useAuthRedirect } from './hooks/useAuthRedirect';
import './index.css';

// 全局认证监听器组件
const GlobalAuthListener: React.FC = () => {
  useAuthRedirect();
  return null;
};

const App: React.FC = () => {
  return (
    <Router>
      <div className="App">
        <GlobalAuthListener />
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/landing1" element={<LandingPage1 />} />
          <Route path="/home" element={<HomePage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/resume" element={<ResumePage />} />
          <Route path="/jobs" element={<JobPage />} />
          <Route path="/jobs/:id" element={<JobPage />} />
          <Route path="/jobs/new" element={<JobPage />} />
          <Route path="/interview" element={<FormalInterviewPage />} />
          <Route path="/formal-interview" element={<FormalInterviewPage />} />
          <Route path="/mock-interview" element={<MockInterviewPage />} />
          <Route path="/interview-record" element={<InterviewRecordPage />} />
          <Route path="/complete" element={<CompletePage />} />
          <Route path="/profile" element={<UserProfilePage />} />
          <Route path="/privacy-policy" element={<PrivacyPolicyPage />} />
          <Route path="/terms-of-use" element={<TermsOfUsePage />} />
          <Route path="/auth/callback" element={<OAuthCallbackPage />} />
          {/* Other routes can be added here */}
          <Route path="/demo" element={<div className="p-8">Demo Page - Coming Soon</div>} />
          <Route path="/contact" element={<div className="p-8">Contact Page - Coming Soon</div>} />
          <Route path="/dashboard" element={<div className="p-8">Dashboard - Coming Soon</div>} />
        </Routes>
      </div>
    </Router>
  );
};

export default App; 