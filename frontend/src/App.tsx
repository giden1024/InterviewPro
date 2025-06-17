import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LandingPage from './pages/LandingPage';
import HomePage from './pages/HomePage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import ResumePage from './pages/ResumePage';
import JobPage from './pages/JobPage';
import CompletePage from './pages/CompletePage';
import MockInterviewPage from './pages/MockInterviewPage';
import UserProfilePage from './pages/UserProfilePage';
import './index.css';

const App: React.FC = () => {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/home" element={<HomePage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/resume" element={<ResumePage />} />
          <Route path="/jobs" element={<JobPage />} />
          <Route path="/jobs/:id" element={<JobPage />} />
          <Route path="/jobs/new" element={<JobPage />} />
          <Route path="/interview" element={<MockInterviewPage />} />
          <Route path="/mock-interview" element={<MockInterviewPage />} />
          <Route path="/complete" element={<CompletePage />} />
          <Route path="/profile" element={<UserProfilePage />} />
          {/* 其他路由可以在这里添加 */}
          <Route path="/demo" element={<div className="p-8">Demo Page - Coming Soon</div>} />
          <Route path="/contact" element={<div className="p-8">Contact Page - Coming Soon</div>} />
          <Route path="/dashboard" element={<div className="p-8">Dashboard - Coming Soon</div>} />
        </Routes>
      </div>
    </Router>
  );
};

export default App; 