import React from 'react';
import { OfferotterHome } from '../components/OfferotterHome';
import { useNavigate } from 'react-router-dom';

const HomePage: React.FC = () => {
  const navigate = useNavigate();

  // API 基础地址配置
  // const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  const handleGetStarted = () => {
    // 直接跳转到Job页面，开始面试准备流程
    navigate('/job');
  };

  const handleWatchDemo = () => {
    // 打开演示页面
    navigate('/demo');
  };

  const handleContactUs = () => {
    // 跳转到联系页面
    navigate('/contact');
  };

  const handleLogin = () => {
    // 跳转到登录页面
    navigate('/login');
  };

  // 自定义统计数据（可以从 API 获取）
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
      heroTitle="InterviewPro AI面试助手"
      heroSubtitle="智能面试练习，实时语音识别，专业简历优化 - 助您轻松获得心仪工作"
      theme="light"
    />
  );
};

export default HomePage; 