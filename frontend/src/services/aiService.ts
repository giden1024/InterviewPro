import { apiClient, ApiResponse } from './api';

export interface AIAnswerResponse {
  question: string;
  answer: string;
  generated_at: string;
}

class AIService {
  async generateAnswer(question: string): Promise<AIAnswerResponse> {
    try {
      const result = await apiClient.post<ApiResponse<AIAnswerResponse>>('/interviews/generate-answer', { question });
      
      if (!result.success) {
        throw new Error(result.message || 'Failed to generate answer');
      }

      return result.data!;
    } catch (error) {
      console.error('AI answer generation failed:', error);
      throw error;
    }
  }
}

export const aiService = new AIService(); 