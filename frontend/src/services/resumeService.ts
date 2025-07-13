import { apiClient } from './api';

export interface Resume {
  id: number;
  user_id: number;
  filename: string;
  original_filename: string;
  file_path: string;
  file_size: number;
  status: 'pending' | 'processing' | 'completed' | 'processed' | 'failed';
  skills: string[];
  experience: string[];
  education: string[];
  contact_info: any;
  work_history: any[];
  parsed_data: any;
  analysis_result: any;
  created_at: string;
  updated_at: string;
  uploaded_at?: string;
}

export interface CreateResumeData {
  file: File;
  filename?: string;
}

export interface ResumeStats {
  total_resumes: number;
  completed_resumes: number;
  pending_resumes: number;
  failed_resumes: number;
  top_skills: Array<{ skill: string; count: number }>;
}

export interface ResumeSearchParams {
  query: string;
  skills?: string[];
  experience_level?: string;
  location?: string;
}

class ResumeService {
  /**
   * 获取简历列表
   */
  async getResumes(params?: {
    page?: number;
    per_page?: number;
    status?: string;
  }): Promise<{
    resumes: Resume[];
    pagination: any;
  }> {
    try {
      const queryParams = new URLSearchParams();
      if (params?.page) queryParams.append('page', params.page.toString());
      if (params?.per_page) queryParams.append('per_page', params.per_page.toString());
      if (params?.status) queryParams.append('status', params.status);
      
      const endpoint = queryParams.toString() ? `/resumes?${queryParams.toString()}` : '/resumes';
      const response: any = await apiClient.get(endpoint);
      
      // 直接返回响应，因为apiClient.get已经解析了JSON
      return response;
    } catch (error) {
      console.error('获取简历列表失败:', error);
      throw error;
    }
  }

  /**
   * 上传简历
   */
  async uploadResume(file: File): Promise<Resume> {
    try {
      const response: any = await apiClient.uploadFile('/resumes', file);
      
      // 检查响应格式并提取简历数据
      if (response.data && response.data.resume) {
        return response.data.resume;
      } else if (response.resume) {
        return response.resume;
      } else if (response.data) {
        return response.data;
      } else {
        // 如果响应格式不符合预期，抛出错误
        console.error('Unexpected response format:', response);
        throw new Error('服务器响应格式错误');
      }
    } catch (error) {
      console.error('上传简历失败:', error);
      throw error;
    }
  }

  /**
   * 获取简历详情
   */
  async getResume(resumeId: number): Promise<Resume> {
    try {
      const response: any = await apiClient.get(`/resumes/${resumeId}`);
      return response.data.resume;
    } catch (error) {
      console.error('获取简历详情失败:', error);
      throw error;
    }
  }

  /**
   * 删除简历
   */
  async deleteResume(resumeId: number): Promise<void> {
    try {
      await apiClient.delete(`/resumes/${resumeId}`);
    } catch (error) {
      console.error('删除简历失败:', error);
      throw error;
    }
  }

  /**
   * 重新解析简历
   */
  async reparseResume(resumeId: number): Promise<Resume> {
    try {
      const response: any = await apiClient.post(`/resumes/${resumeId}/reparse`);
      return response.data.resume;
    } catch (error) {
      console.error('重新解析简历失败:', error);
      throw error;
    }
  }

  /**
   * 获取简历统计
   */
  async getResumeStats(): Promise<ResumeStats> {
    try {
      const response: any = await apiClient.get('/resumes/stats');
      return response.data;
    } catch (error) {
      console.error('获取简历统计失败:', error);
      throw error;
    }
  }

  /**
   * 下载简历
   */
  async downloadResume(resumeId: number): Promise<Blob> {
    try {
      // 需要使用原生fetch来处理blob响应
      const token = localStorage.getItem('access_token');
      const response = await fetch(`http://localhost:5001/api/v1/resumes/${resumeId}/download`, {
        method: 'GET',
        headers: {
          'Authorization': token ? `Bearer ${token}` : '',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      return await response.blob();
    } catch (error) {
      console.error('下载简历失败:', error);
      throw error;
    }
  }

  /**
   * 预览简历
   */
  async previewResume(resumeId: number): Promise<{
    preview_url: string;
    preview_data: any;
  }> {
    try {
      const response: any = await apiClient.get(`/resumes/${resumeId}/preview`);
      return response.data;
    } catch (error) {
      console.error('预览简历失败:', error);
      throw error;
    }
  }

  /**
   * 分析简历
   */
  async analyzeResume(resumeId: number, options?: {
    include_suggestions?: boolean;
    include_score?: boolean;
  }): Promise<{
    analysis: any;
    suggestions: any[];
    score: number;
  }> {
    try {
      const response: any = await apiClient.post(`/resumes/${resumeId}/analyze`, options);
      return response.data;
    } catch (error) {
      console.error('分析简历失败:', error);
      throw error;
    }
  }

  /**
   * 搜索简历
   */
  async searchResumes(params: ResumeSearchParams): Promise<{
    resumes: Resume[];
    total: number;
  }> {
    try {
      const response: any = await apiClient.post('/resumes/search', params);
      return response.data;
    } catch (error) {
      console.error('搜索简历失败:', error);
      throw error;
    }
  }

  /**
   * 批量处理简历
   */
  async batchProcessResumes(resumeIds: number[], action: string): Promise<{
    success: number;
    failed: number;
    results: any[];
  }> {
    try {
      const response: any = await apiClient.post('/resumes/batch', {
        resume_ids: resumeIds,
        action
      });
      return response.data;
    } catch (error) {
      console.error('批量处理简历失败:', error);
      throw error;
    }
  }

  /**
   * 导出简历
   */
  async exportResumes(format: 'json' | 'csv' | 'pdf' = 'json', resumeIds?: number[]): Promise<Blob> {
    try {
      // 需要使用原生fetch来处理blob响应
      const token = localStorage.getItem('access_token');
      const response = await fetch(`http://localhost:5001/api/v1/resumes/export`, {
        method: 'POST',
        headers: {
          'Authorization': token ? `Bearer ${token}` : '',
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          format,
          resume_ids: resumeIds
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      return await response.blob();
    } catch (error) {
      console.error('导出简历失败:', error);
      throw error;
    }
  }
}

// 导出单例实例
export const resumeService = new ResumeService(); 