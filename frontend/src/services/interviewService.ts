import { apiClient } from './api';

export interface InterviewSession {
  id: number;
  user_id?: number;
  resume_id?: number;
  session_id: string;
  title: string;
  interview_type: 'technical' | 'hr' | 'comprehensive' | 'mock';
  status: 'created' | 'in_progress' | 'completed' | 'paused' | 'cancelled';
  total_questions: number;
  current_question?: number;
  completed_questions?: number;
  total_score?: number | null;
  difficulty_distribution?: Record<string, number>;
  type_distribution?: Record<string, number>;
  started_at?: string | null;
  completed_at?: string | null;
  created_at: string;
  updated_at?: string;
}

export interface Question {
  id: number;
  question_text: string;
  question_type: string;
  difficulty: 'easy' | 'medium' | 'hard';
  category: string;
  tags: string[];
  expected_answer?: string;
  evaluation_criteria?: Record<string, any>;
  ai_context?: Record<string, any>;
  created_at: string;
}

export interface Answer {
  id: number;
  question_id: number;
  session_id: number;
  answer_text?: string;
  response_time?: number;
  audio_url?: string;
  transcript?: string;
  evaluation_score?: number;
  feedback?: string;
  created_at: string;
}

export interface CreateInterviewData {
  resume_id: number;
  interview_type: 'technical' | 'hr' | 'comprehensive' | 'mock';
  total_questions?: number;
  custom_title?: string;
  difficulty_distribution?: Record<string, number>;
  type_distribution?: Record<string, number>;
}

export interface SubmitAnswerData {
  question_id: number;
  answer_text?: string;
  response_time?: number;
  audio_file?: File;
}

export interface InterviewStats {
  total_interviews: number;
  completed_interviews: number;
  average_score: number;
  interview_types: Array<{ type: string; count: number }>;
  performance_trend: Array<{ date: string; score: number }>;
}

class InterviewService {
  /**
   * 创建面试会话
   */
  async createInterview(data: CreateInterviewData): Promise<{
    session: InterviewSession;
    session_id: string;
  }> {
    try {
      const response: any = await apiClient.post('/interviews', data);
      return response.data;
    } catch (error) {
      console.error('创建面试会话失败:', error);
      throw error;
    }
  }

  /**
   * 获取面试会话列表
   */
  async getInterviews(params?: {
    page?: number;
    per_page?: number;
    status?: string;
  }): Promise<{
    sessions: InterviewSession[];
    pagination: any;
  }> {
    try {
      const queryParams = new URLSearchParams();
      if (params?.page) queryParams.append('page', params.page.toString());
      if (params?.per_page) queryParams.append('per_page', params.per_page.toString());
      if (params?.status) queryParams.append('status', params.status);
      
      const endpoint = queryParams.toString() ? `/interviews?${queryParams.toString()}` : '/interviews';
      const response: any = await apiClient.get(endpoint);
      return response.data;
    } catch (error) {
      console.error('获取面试列表失败:', error);
      throw error;
    }
  }

  /**
   * 获取面试会话详情
   */
  async getInterview(sessionId: string): Promise<{
    session: InterviewSession;
    questions: Question[];
    total_questions: number;
  }> {
    try {
      const response: any = await apiClient.get(`/interviews/${sessionId}`);
      return response.data;
    } catch (error) {
      console.error('获取面试详情失败:', error);
      throw error;
    }
  }

  /**
   * 开始面试会话
   */
  async startInterview(sessionId: string): Promise<{
    session: InterviewSession;
    next_question: Question;
  }> {
    try {
      const response: any = await apiClient.post(`/interviews/${sessionId}/start`);
      return response.data;
    } catch (error) {
      console.error('开始面试失败:', error);
      throw error;
    }
  }

  /**
   * 获取下一个问题
   */
  async getNextQuestion(sessionId: string): Promise<Question | { completed: true; message: string }> {
    try {
      const response: any = await apiClient.get(`/interviews/${sessionId}/next`);
      return response.data;
    } catch (error) {
      console.error('获取下一个问题失败:', error);
      throw error;
    }
  }

  /**
   * 提交答案
   */
  async submitAnswer(sessionId: string, data: SubmitAnswerData): Promise<{
    answer: Answer;
    next_question?: Question;
    completed?: boolean;
  }> {
    try {
      const response: any = await apiClient.post(`/interviews/${sessionId}/answer`, data);
      return response.data;
    } catch (error) {
      console.error('提交答案失败:', error);
      throw error;
    }
  }

  /**
   * 结束面试会话
   */
  async endInterview(sessionId: string): Promise<{
    session: InterviewSession;
    summary: any;
  }> {
    try {
      const response: any = await apiClient.post(`/interviews/${sessionId}/end`);
      return response.data;
    } catch (error) {
      console.error('结束面试失败:', error);
      throw error;
    }
  }

  /**
   * 删除面试会话
   */
  async deleteInterview(sessionId: string): Promise<void> {
    try {
      await apiClient.delete(`/interviews/${sessionId}`);
    } catch (error) {
      console.error('删除面试会话失败:', error);
      throw error;
    }
  }

  /**
   * 重新生成问题
   */
  async regenerateQuestions(sessionId: string, params?: {
    total_questions?: number;
    difficulty_distribution?: Record<string, number>;
    type_distribution?: Record<string, number>;
  }): Promise<{
    session: InterviewSession;
    questions: Question[];
  }> {
    try {
      const response: any = await apiClient.post(`/interviews/${sessionId}/regenerate`, params || {});
      return response.data;
    } catch (error) {
      console.error('重新生成问题失败:', error);
      throw error;
    }
  }

  /**
   * 获取面试统计
   */
  async getInterviewStats(): Promise<InterviewStats> {
    try {
      const response: any = await apiClient.get('/interviews/statistics');
      return response.data;
    } catch (error) {
      console.error('获取面试统计失败:', error);
      throw error;
    }
  }

  /**
   * 获取面试类型列表
   */
  async getInterviewTypes(): Promise<Array<{
    type: string;
    name: string;
    description: string;
    default_questions: number;
  }>> {
    try {
      const response: any = await apiClient.get('/interviews/types');
      return response.data.types;
    } catch (error) {
      console.error('获取面试类型失败:', error);
      throw error;
    }
  }

  /**
   * 暂停面试
   */
  async pauseInterview(sessionId: string): Promise<{
    session: InterviewSession;
  }> {
    try {
      const response: any = await apiClient.post(`/interviews/${sessionId}/pause`);
      return response.data;
    } catch (error) {
      console.error('暂停面试失败:', error);
      throw error;
    }
  }

  /**
   * 恢复面试
   */
  async resumeInterview(sessionId: string): Promise<{
    session: InterviewSession;
    current_question: Question;
  }> {
    try {
      const response: any = await apiClient.post(`/interviews/${sessionId}/resume`);
      return response.data;
    } catch (error) {
      console.error('恢复面试失败:', error);
      throw error;
    }
  }

  /**
   * 获取面试答案列表
   */
  async getInterviewAnswers(sessionId: string): Promise<Answer[]> {
    try {
      const response: any = await apiClient.get(`/interviews/${sessionId}/answers`);
      return response.data.answers;
    } catch (error) {
      console.error('获取面试答案失败:', error);
      throw error;
    }
  }

  /**
   * 上传音频答案
   */
  async uploadAudioAnswer(sessionId: string, questionId: number, audioFile: File): Promise<{
    answer: Answer;
    transcript?: string;
  }> {
    try {
      const formData = new FormData();
      formData.append('audio', audioFile);
      formData.append('question_id', questionId.toString());

      // 注意：这里需要扩展 ApiClient 来支持 FormData 和自定义 headers
      const token = localStorage.getItem('access_token');
      const response = await fetch(`http://localhost:5001/api/v1/interviews/${sessionId}/audio-answer`, {
        method: 'POST',
        headers: {
          'Authorization': token ? `Bearer ${token}` : '',
        },
        body: formData,
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      const result = await response.json();
      return result.data;
    } catch (error) {
      console.error('上传音频答案失败:', error);
      throw error;
    }
  }
}

// 导出单例实例
export const interviewService = new InterviewService(); 