import { useState, useCallback, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { questionService } from '../services/questionService';

export interface Job {
  id: string;
  title: string;
  isSelected?: boolean;
}

export interface QuestionWithAnswer {
  id: number;
  question_text: string;
  question_type: string;
  difficulty: string;
  category: string;
  tags: string[];
  latest_answer?: {
    id: number;
    answer_text: string;
    score?: number;
    answered_at: string;
  };
  created_at: string;
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

  const [questionsWithAnswers, setQuestionsWithAnswers] = useState<QuestionWithAnswer[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [stats, setStats] = useState<InterviewStats>({
    mockMinutes: 15,
    formalMinutes: 30,
    totalQuestions: 0,
    answeredQuestions: 0
  });

  const [activeTab, setActiveTab] = useState<'questions' | 'records'>('questions');

  // 加载问题和答案数据
  const loadQuestionsWithAnswers = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      const response = await questionService.getQuestionsWithAnswers({
        page: 1,
        per_page: 10,
        has_answers: true
      });
      
      setQuestionsWithAnswers(response.questions);
      setStats(prev => ({
        ...prev,
        totalQuestions: response.pagination.total,
        answeredQuestions: response.questions.filter(q => q.latest_answer).length
      }));
    } catch (error) {
      console.error('加载问题和答案失败:', error);
      setError('加载数据失败，请重试');
    } finally {
      setIsLoading(false);
    }
  }, []);

  // 初始化加载数据
  useEffect(() => {
    loadQuestionsWithAnswers();
  }, [loadQuestionsWithAnswers]);

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

  const handleQuestionEdit = useCallback((questionId: number) => {
    console.log('Edit question:', questionId);
    // 跳转到编辑页面
    navigate(`/questions/${questionId}/edit`);
  }, [navigate]);

  const handleQuestionDelete = useCallback(async (questionId: number) => {
    try {
      if (window.confirm('确定要删除这个问题吗？此操作不可撤销。')) {
        await questionService.deleteQuestion(questionId);
        // 重新加载数据
        await loadQuestionsWithAnswers();
        alert('问题删除成功');
      }
    } catch (error) {
      console.error('删除问题失败:', error);
      alert('删除问题失败，请重试');
    }
  }, [loadQuestionsWithAnswers]);

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
    questionsWithAnswers,
    stats,
    activeTab,
    isLoading,
    error,
    
    // 交互方法
    handleAddNewJob,
    handleSelectJob,
    handleQuestionEdit,
    handleQuestionDelete,
    handleUpgrade,
    handleStartMockInterview,
    handleStartFormalInterview,
    handleAddQuestion,
    handleTabChange,
    loadQuestionsWithAnswers
  };
}; 