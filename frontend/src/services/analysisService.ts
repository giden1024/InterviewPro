import { apiClient } from './api';

export interface AnalysisResult {
  session_id: string;
  overall_score: number;
  category_scores: Record<string, number>;
  strengths: string[];
  weaknesses: string[];
  recommendations: string[];
  performance_metrics: {
    avg_response_time: number;
    completion_rate: number;
    technical_accuracy: number;
    communication_clarity: number;
  };
  created_at: string;
}

export interface InterviewReport {
  session_info: {
    session_id: string;
    title: string;
    interview_type: string;
    duration: number;
    completed_at: string;
  };
  summary: {
    overall_score: number;
    grade: string;
    percentile: number;
    total_questions: number;
    answered_questions: number;
  };
  analysis: AnalysisResult;
}

export interface UserStatistics {
  total_interviews: number;
  average_score: number;
  improvement_trend: Array<{ date: string; score: number }>;
  performance_by_type: Record<string, {
    count: number;
    average_score: number;
    best_score: number;
  }>;
}

class AnalysisService {
  /**
   * Analyze interview session results
   */
  async analyzeSession(sessionId: string): Promise<AnalysisResult> {
    try {
      const response: any = await apiClient.get(`/analysis/session/${sessionId}`);
      return response.data;
    } catch (error) {
      console.error('Failed to analyze interview session:', error);
      throw error;
    }
  }

      /**
     * Generate interview report
     */
  async generateReport(sessionId: string): Promise<InterviewReport> {
    try {
      const response: any = await apiClient.get(`/analysis/report/${sessionId}`);
      return response.data;
    } catch (error) {
      console.error('Failed to generate interview report:', error);
      throw error;
    }
  }

      /**
     * Get user interview statistics
     */
  async getUserStatistics(params?: {
    days?: number;
    interview_type?: string;
  }): Promise<UserStatistics> {
    try {
      const queryParams = new URLSearchParams();
      if (params?.days) queryParams.append('days', params.days.toString());
      if (params?.interview_type) queryParams.append('interview_type', params.interview_type);
      
      const endpoint = queryParams.toString() ? `/analysis/statistics?${queryParams.toString()}` : '/analysis/statistics';
      const response: any = await apiClient.get(endpoint);
      return response.data;
    } catch (error) {
      console.error('Failed to get user statistics:', error);
      throw error;
    }
  }

      /**
     * Compare multiple interview results
     */
  async compareInterviews(sessionIds: string[]): Promise<any> {
    try {
      const response: any = await apiClient.post('/analysis/comparison', {
        session_ids: sessionIds
      });
      return response.data;
    } catch (error) {
      console.error('Failed to compare interview results:', error);
      throw error;
    }
  }

      /**
     * Export analysis results
     */
  async exportAnalysis(sessionId: string, format: 'pdf' | 'json' | 'csv' = 'pdf'): Promise<Blob> {
    try {
      const response = await fetch(`http://localhost:5001/api/v1/analysis/export/${sessionId}?format=${format}`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      return await response.blob();
    } catch (error) {
      console.error('Failed to export analysis results:', error);
      throw error;
    }
  }
}

  // Export singleton instance
export const analysisService = new AnalysisService(); 