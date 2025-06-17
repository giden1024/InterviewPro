import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';

export interface Job {
  id: string;
  title: string;
  isSelected?: boolean;
}

export interface Question {
  id: string;
  title: string;
  content: string;
  isAnswered?: boolean;
}

export interface InterviewStats {
  mockMinutes: number;
  formalMinutes: number;
  totalQuestions: number;
  answeredQuestions: number;
}

export const useHomePage = () => {
  const navigate = useNavigate();
  
  // 状态管理
  const [jobs, setJobs] = useState<Job[]>([
    { id: '1', title: 'Product Manager', isSelected: true },
    { id: '2', title: 'Marketing Planner', isSelected: false }
  ]);

  const [questions] = useState<Question[]>([
    {
      id: '1',
      title: 'How would you design a campaign to recruit new live streamers in a market where live streaming is still stigmatized?',
      content: "To tackle stigma, I'd focus on reframing live streaming as a tool for ​​community empowerment​​ rather than just entertainment. For example, in Indonesia, I'd partner with local religious leaders or educators to launch a campaign like 'Knowledge Live,' where respected figures (e.g., Quran teachers, traditional artisans) demonstrate how streaming helps them share skills or preserve culture. To incentivize participation, I'd create a 'First Stream Kit'—offering free lighting filters and halal-compliant............",
      isAnswered: true
    },
    {
      id: '2', 
      title: 'How would you measure the success of a live streamer recruitment campaign?',
      content: "Quality of adoption​​: % of new streamers who complete ≥3 streams (measuring retention, not just interest).Sentiment shift​​: Pre/post-campaign surveys on perceptions (e.g., 'Is streaming a respectable career?').Efficiency​​: Cost-per-engaged-streamer (CPES), factoring in training/resources provided.For example, if we recruit 1,000 streamers but only 200 stay active after a month, I'd investigate pain points (e.g., monetization clarity) and iterate. I'd also benchmark against local competitors' retention rates to contextualize results.",
      isAnswered: true
    }
  ]);

  const [stats] = useState<InterviewStats>({
    mockMinutes: 15,
    formalMinutes: 30,
    totalQuestions: 10,
    answeredQuestions: 2
  });

  const [activeTab, setActiveTab] = useState<'questions' | 'records'>('questions');

  // 交互事件处理
  const handleAddNewJob = useCallback(() => {
    navigate('/job');
  }, [navigate]);

  const handleSelectJob = useCallback((jobId: string) => {
    setJobs(prev => prev.map(job => ({
      ...job,
      isSelected: job.id === jobId
    })));
  }, []);

  const handleQuestionEdit = useCallback((questionId: string) => {
    console.log('Edit question:', questionId);
    // TODO: 实现编辑功能
  }, []);

  const handleQuestionDelete = useCallback((questionId: string) => {
    console.log('Delete question:', questionId);
    // TODO: 实现删除功能
  }, []);

  const handleUpgrade = useCallback(() => {
    navigate('/pricing');
  }, [navigate]);

  const handleStartMockInterview = useCallback(() => {
    navigate('/mock-interview');
  }, [navigate]);

  const handleStartFormalInterview = useCallback(() => {
    navigate('/mock-interview');
  }, [navigate]);

  const handleAddQuestion = useCallback(() => {
    navigate('/questions/create');
  }, [navigate]);

  const handleTabChange = useCallback((tab: 'questions' | 'records') => {
    setActiveTab(tab);
    if (tab === 'records') {
      navigate('/interview/records');
    }
  }, [navigate]);

  return {
    // 状态
    jobs,
    questions,
    stats,
    activeTab,
    
    // 交互方法
    handleAddNewJob,
    handleSelectJob,
    handleQuestionEdit,
    handleQuestionDelete,
    handleUpgrade,
    handleStartMockInterview,
    handleStartFormalInterview,
    handleAddQuestion,
    handleTabChange
  };
}; 