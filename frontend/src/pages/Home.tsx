import React from 'react';
import { OfferotterHome } from '../components/OfferotterHome';
import { useNavigate } from 'react-router-dom';

const HomePage: React.FC = () => {
  const navigate = useNavigate();

  // API base URL configuration
  // const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  const handleGetStarted = () => {
    // Redirect to Jobs page to start interview preparation process
    navigate('/jobs');
  };

  const handleWatchDemo = () => {
    // Open demo page
    navigate('/demo');
  };

  const handleContactUs = () => {
    // Redirect to contact page
    navigate('/contact');
  };

  const handleLogin = () => {
    // Redirect to login page
    navigate('/login');
  };

  // Custom statistics data (can be fetched from API)
  const statistics = {
    resumesAnalyzed: '380,000+',
    interviewParticipants: '1,200,000',
  };

  return (
    <OfferotterHome
      onGetStarted={handleGetStarted}
      onWatchDemo={handleWatchDemo}
      onContactUs={handleContactUs}
      onLogin={handleLogin}
      statistics={statistics}
      heroTitle="InterviewPro AI Interview Assistant"
      heroSubtitle="Smart interview practice, real-time speech recognition, professional resume optimization - helping you easily land your dream job"
      theme="light"
    />
  );
};

export default HomePage; 