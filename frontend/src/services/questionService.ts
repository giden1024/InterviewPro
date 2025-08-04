import { apiClient } from './api';

export interface Question {
  id: number;
  resume_id: number;
  user_id: number;
  session_id?: number;
  question_text: string;
  question_type: 'technical' | 'behavioral' | 'situational' | 'experience' | 'culture_fit';
  difficulty: 'easy' | 'medium' | 'hard';
  category: string;
  tags: string[];
  expected_answer?: string;
  evaluation_criteria?: Record<string, any>;
  ai_context?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface InterviewSession {
  id: number;
  user_id: number;
  resume_id: number;
  session_id: string;
  title: string;
  interview_type: 'technical' | 'hr' | 'comprehensive' | 'mock';
  status: 'created' | 'ready' | 'in_progress' | 'completed' | 'cancelled';
  total_questions: number;
  difficulty_distribution?: Record<string, number>;
  type_distribution?: Record<string, number>;
  created_at: string;
  updated_at: string;
}

export interface GenerateQuestionsData {
  resume_id: number;
  session_id: string;  // 现在必须提供session_id
  interview_type?: 'technical' | 'hr' | 'comprehensive' | 'mock';  // 改为可选
  total_questions?: number;
  difficulty_distribution?: Record<string, number>;
  type_distribution?: Record<string, number>;
  title?: string;
}

export interface AsyncTaskStatus {
  task_id: string;
  state: 'PENDING' | 'PROGRESS' | 'SUCCESS' | 'FAILURE';
  current?: number;
  total?: number;
  status?: string;
  questions?: Question[];
  from_cache?: boolean;
  generated_at?: string;
  error?: string;
}

export interface QuestionStats {
  total_questions: number;
  by_difficulty: Record<string, number>;
  by_type: Record<string, number>;
  by_category: Record<string, number>;
  recent_generation_count: number;
}

class QuestionService {
  /**
   * 获取用户的问题列表
   */
  async getQuestions(params?: {
    page?: number;
    per_page?: number;
    type?: string;
    difficulty?: string;
    category?: string;
  }): Promise<{
    questions: Question[];
    pagination: {
      page: number;
      per_page: number;
      total: number;
      pages: number;
      has_next: boolean;
      has_prev: boolean;
    };
  }> {
    try {
      const queryParams = new URLSearchParams();
      if (params?.page) queryParams.append('page', params.page.toString());
      if (params?.per_page) queryParams.append('per_page', params.per_page.toString());
      if (params?.type) queryParams.append('type', params.type);
      if (params?.difficulty) queryParams.append('difficulty', params.difficulty);
      if (params?.category) queryParams.append('category', params.category);
      
      const endpoint = queryParams.toString() ? `/questions?${queryParams.toString()}` : '/questions';
      const response: any = await apiClient.get(endpoint);
      return response.data;
    } catch (error) {
      console.error('获取问题列表失败:', error);
      throw error;
    }
  }

  /**
   * 基于简历生成面试问题（同步）
   */
  async generateQuestions(data: GenerateQuestionsData): Promise<{
    session: InterviewSession;
    questions: Question[];
    stats: {
      total_generated: number;
      resume_id: number;
      resume_filename: string;
    };
  }> {
    try {
      console.log('🔍 [DEBUG] generateQuestions被调用');
      console.log('🔍 [DEBUG] 请求数据:', JSON.stringify(data, null, 2));
      console.log('🔍 [DEBUG] 数据类型检查:');
      console.log('  - resume_id:', typeof data.resume_id, data.resume_id);
      console.log('  - session_id:', typeof data.session_id, data.session_id);
      console.log('  - interview_type:', typeof data.interview_type, data.interview_type);
      console.log('  - total_questions:', typeof data.total_questions, data.total_questions);
      
      const response: any = await apiClient.post('/questions/generate', data);
      console.log('🔍 [DEBUG] API响应成功:', response);
      return response.data;
    } catch (error) {
      console.error('🔍 [DEBUG] generateQuestions失败，错误详情:', error);
      console.error('🔍 [DEBUG] 错误类型:', typeof error);
      console.error('🔍 [DEBUG] 错误对象键:', Object.keys(error as any));
      if ((error as any).response) {
        console.error('🔍 [DEBUG] 响应状态:', (error as any).response.status);
        console.error('🔍 [DEBUG] 响应数据:', (error as any).response.data);
        console.error('🔍 [DEBUG] 响应头:', (error as any).response.headers);
      }
      console.error('生成问题失败:', error);
      throw error;
    }
  }

  /**
   * 异步生成面试问题
   */
  async generateQuestionsAsync(data: GenerateQuestionsData): Promise<{
    session_id: string;
    questions: Question[];
    total_questions: number;
    status: string;
    message: string;
  }> {
    try {
      const response: any = await apiClient.post('/questions/generate-async', data);
      return response.data;
    } catch (error) {
      console.error('启动异步问题生成失败:', error);
      throw error;
    }
  }

  /**
   * 获取异步任务状态
   */
  async getTaskStatus(taskId: string): Promise<AsyncTaskStatus> {
    try {
      const response: any = await apiClient.get(`/questions/task-status/${taskId}`);
      return response.data;
    } catch (error) {
      console.error('获取任务状态失败:', error);
      throw error;
    }
  }

  /**
   * 获取特定会话的问题
   */
  async getSessionQuestions(sessionId: string): Promise<{
    session: InterviewSession;
    questions: Question[];
    total_questions: number;
  }> {
    try {
      const response: any = await apiClient.get(`/questions/session/${sessionId}`);
      return response.data;
    } catch (error) {
      console.error('获取会话问题失败:', error);
      throw error;
    }
  }

  /**
   * 获取面试会话列表
   */
  async getInterviewSessions(params?: {
    page?: number;
    per_page?: number;
    status?: string;
    interview_type?: string;
  }): Promise<{
    sessions: InterviewSession[];
    pagination: any;
  }> {
    try {
      const queryParams = new URLSearchParams();
      if (params?.page) queryParams.append('page', params.page.toString());
      if (params?.per_page) queryParams.append('per_page', params.per_page.toString());
      if (params?.status) queryParams.append('status', params.status);
      if (params?.interview_type) queryParams.append('interview_type', params.interview_type);
      
      const endpoint = queryParams.toString() ? `/questions/sessions?${queryParams.toString()}` : '/questions/sessions';
      const response: any = await apiClient.get(endpoint);
      return response.data;
    } catch (error) {
      console.error('获取面试会话列表失败:', error);
      throw error;
    }
  }

  /**
   * 获取问题统计
   */
  async getQuestionStats(): Promise<QuestionStats> {
    try {
      const response: any = await apiClient.get('/questions/stats');
      return response.data;
    } catch (error) {
      console.error('获取问题统计失败:', error);
      throw error;
    }
  }

  /**
   * 获取问题详情
   */
  async getQuestionDetail(questionId: number): Promise<{
    question: Question;
    related_questions: Question[];
    usage_history: Array<{
      session_id: string;
      used_at: string;
      answer_quality?: number;
    }>;
  }> {
    try {
      const response: any = await apiClient.get(`/questions/${questionId}`);
      return response.data;
    } catch (error) {
      console.error('获取问题详情失败:', error);
      throw error;
    }
  }

  /**
   * 测试问题生成器
   */
  async testQuestionGenerator(params?: {
    resume_text?: string;
    job_description?: string;
    interview_type?: string;
    count?: number;
  }): Promise<{
    generated_questions: Question[];
    generation_stats: {
      time_taken: number;
      ai_model_used: string;
      fallback_used: boolean;
    };
    quality_metrics: {
      relevance_score: number;
      difficulty_balance: Record<string, number>;
      type_diversity: Record<string, number>;
    };
  }> {
    try {
      const response: any = await apiClient.post('/questions/test-generator', params || {});
      return response.data;
    } catch (error) {
      console.error('测试问题生成器失败:', error);
      throw error;
    }
  }

  /**
   * 更新问题
   */
  async updateQuestion(questionId: number, data: {
    question_text?: string;
    question_type?: string;
    difficulty?: string;
    category?: string;
    tags?: string[];
    expected_answer?: string;
    evaluation_criteria?: Record<string, any>;
  }): Promise<Question> {
    try {
      const response: any = await apiClient.put(`/questions/${questionId}`, data);
      return response.data;
    } catch (error) {
      console.error('更新问题失败:', error);
      throw error;
    }
  }

  /**
   * 删除问题
   */
  async deleteQuestion(questionId: number): Promise<void> {
    try {
      await apiClient.post(`/questions/${questionId}/delete`, {}); // 使用POST模拟DELETE
    } catch (error) {
      console.error('删除问题失败:', error);
      throw error;
    }
  }

  /**
   * 删除面试会话
   */
  async deleteSession(sessionId: string): Promise<void> {
    try {
      await apiClient.post(`/questions/sessions/${sessionId}/delete`, {}); // 使用POST模拟DELETE
    } catch (error) {
      console.error('删除面试会话失败:', error);
      throw error;
    }
  }

  /**
   * 收藏问题
   */
  async favoriteQuestion(questionId: number): Promise<void> {
    try {
      await apiClient.post(`/questions/${questionId}/favorite`);
    } catch (error) {
      console.error('收藏问题失败:', error);
      throw error;
    }
  }

  /**
   * 取消收藏问题
   */
  async unfavoriteQuestion(questionId: number): Promise<void> {
    try {
      await apiClient.post(`/questions/${questionId}/unfavorite`);
    } catch (error) {
      console.error('取消收藏问题失败:', error);
      throw error;
    }
  }

  /**
   * 获取问题的答案
   */
  async getQuestionAnswers(questionId: number): Promise<{
    question: Question;
    answers: Array<{
      id: number;
      answer_text: string;
      score?: number;
      ai_feedback?: Record<string, any>;
      response_time?: number;
      answered_at: string;
    }>;
  }> {
    try {
      const response: any = await apiClient.get(`/questions/${questionId}/answers`);
      return response.data;
    } catch (error) {
      console.error('获取问题答案失败:', error);
      throw error;
    }
  }

  /**
   * 获取用户的问题和答案列表（用于主页显示）
   */
  async getQuestionsWithAnswers(params?: {
    page?: number;
    per_page?: number;
    has_answers?: boolean;
  }): Promise<{
    questions: Array<Question & {
      latest_answer?: {
        id: number;
        answer_text: string;
        score?: number;
        answered_at: string;
      };
    }>;
    pagination: {
      page: number;
      per_page: number;
      total: number;
      pages: number;
      has_next: boolean;
      has_prev: boolean;
    };
  }> {
    try {
      const queryParams = new URLSearchParams();
      if (params?.page) queryParams.append('page', params.page.toString());
      if (params?.per_page) queryParams.append('per_page', params.per_page.toString());
      if (params?.has_answers !== undefined) queryParams.append('has_answers', params.has_answers.toString());
      
      const endpoint = queryParams.toString() ? `/questions/with-answers?${queryParams.toString()}` : '/questions/with-answers';
      const response: any = await apiClient.get(endpoint);
      return response.data;
    } catch (error) {
      console.error('获取问题和答案列表失败:', error);
      throw error;
    }
  }

  /**
   * 搜索问题
   */
  async searchQuestions(query: string, filters?: {
    type?: string;
    difficulty?: string;
    category?: string;
    tags?: string[];
  }): Promise<{
    questions: Question[];
    total: number;
    search_stats: {
      query: string;
      results_count: number;
      search_time: number;
    };
  }> {
    try {
      const response: any = await apiClient.post('/questions/search', {
        query,
        filters
      });
      return response.data;
    } catch (error) {
      console.error('搜索问题失败:', error);
      throw error;
    }
  }

  /**
   * 实时生成问题的AI参考答案
   */
  async generateAIReferenceAnswer(questionId: number, userContext?: Record<string, any>): Promise<{
    question_id: number;
    question_text: string;
    ai_reference_answer: {
      sample_answer: string;
      reference_answer: string;
      key_points: string[];
      structure_tips: string;
      example_scenarios: string[];
      dos_and_donts: {
        dos: string[];
        donts: string[];
      };
      generated_by: string;
      model?: string;
      question_type: string;
      difficulty: string;
    };
    generated_at: string;
    generation_context: {
      question_type: string;
      difficulty: string;
      category: string;
    };
  }> {
    try {
      const response: any = await apiClient.post(`/questions/${questionId}/generate-reference`, {
        user_context: userContext || {}
      });
      return response.data;
    } catch (error) {
      console.error('生成AI参考答案失败:', error);
      throw error;
    }
  }

  /**
   * 批量生成多个问题的AI参考答案
   */
  async batchGenerateAIReferenceAnswers(questionIds: number[], userContext?: Record<string, any>): Promise<{
    results: Array<{
      question_id: number;
      question_text?: string;
      ai_reference_answer?: any;
      status: 'success' | 'error';
      error?: string;
    }>;
    total_processed: number;
    successful: number;
    failed: number;
    generated_at: string;
  }> {
    try {
      const response: any = await apiClient.post('/questions/batch-generate-references', {
        question_ids: questionIds,
        user_context: userContext || {}
      });
      return response.data;
    } catch (error) {
      console.error('批量生成AI参考答案失败:', error);
      throw error;
    }
  }
}

// 导出单例实例
export const questionService = new QuestionService(); 