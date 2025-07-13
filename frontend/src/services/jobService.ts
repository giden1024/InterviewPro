import { apiClient } from './api';

export interface Job {
  id: number;
  user_id: number;
  resume_id?: number;
  title: string;
  company: string;
  description: string;
  requirements: string[];
  responsibilities: string[];
  salary_range: string;
  location: string;
  remote_allowed: boolean;
  job_type: 'full-time' | 'part-time' | 'contract' | 'internship' | 'freelance';
  status: 'active' | 'inactive' | 'archived';
  source_url: string;
  source_type: string;
  skills_required: string[];
  experience_level: string;
  match_score?: number;
  match_details?: any;
  parsed_data?: any;
  resume?: any;  // 关联的简历信息
  created_at: string;
  updated_at: string;
}

export interface JobTemplate {
  id: number;
  title: string;
  category: string;
  description: string;
  skills: string[];
  experience_level: string;
}

export interface CreateJobData {
  title: string;
  company?: string;
  description?: string;
  resume_id?: number;
  requirements?: string[];
  responsibilities?: string[];
  salary_range?: string;
  location?: string;
  remote_allowed?: boolean;
  job_type?: string;
  source_url?: string;
  skills_required?: string[];
  experience_level?: string;
}

export interface JobsResponse {
  jobs: Job[];
  pagination: {
    page: number;
    per_page: number;
    total: number;
    pages: number;
    has_next: boolean;
    has_prev: boolean;
  };
}

export interface JobStats {
  total_jobs: number;
  active_jobs: number;
  job_types: Array<{ type: string; count: number }>;
  experience_levels: Array<{ level: string; count: number }>;
}

class JobService {
  /**
   * 创建职位
   */
  async createJob(jobData: CreateJobData): Promise<Job> {
    try {
      const response = await apiClient.post('/jobs', jobData);
      return (response as any).data.job;
    } catch (error) {
      console.error('创建职位失败:', error);
      throw error;
    }
  }

  /**
   * 获取职位列表
   */
  async getJobs(params?: {
    page?: number;
    per_page?: number;
    status?: string;
    search?: string;
  }): Promise<JobsResponse> {
    try {
      // 构建查询参数
      const queryParams = new URLSearchParams();
      if (params?.page) queryParams.append('page', params.page.toString());
      if (params?.per_page) queryParams.append('per_page', params.per_page.toString());
      if (params?.status) queryParams.append('status', params.status);
      if (params?.search) queryParams.append('search', params.search);
      
      const endpoint = queryParams.toString() ? `/jobs?${queryParams.toString()}` : '/jobs';
      const response = await apiClient.get(endpoint);
      return (response as any).data;
    } catch (error) {
      console.error('获取职位列表失败:', error);
      throw error;
    }
  }

  /**
   * 获取职位详情
   */
  async getJob(jobId: number): Promise<Job> {
    try {
      const response = await apiClient.get(`/jobs/${jobId}`);
      return (response as any).data.job;
    } catch (error) {
      console.error('获取职位详情失败:', error);
      throw error;
    }
  }

  /**
   * 更新职位
   */
  async updateJob(jobId: number, jobData: Partial<CreateJobData>): Promise<Job> {
    const response = await apiClient.post(`/jobs/${jobId}`, jobData); // 使用POST模拟PUT
    return (response as any).data.job;
  }

  /**
   * 删除职位
   */
  async deleteJob(jobId: number): Promise<void> {
    await apiClient.post(`/jobs/${jobId}/delete`, {}); // 使用POST模拟DELETE
  }

  /**
   * 分析职位URL
   */
  async analyzeJobUrl(url: string): Promise<{ job: Job; parsing_result: any }> {
    try {
      const response: any = await apiClient.post('/jobs/analyze-url', { url });
      return response.data;
    } catch (error) {
      console.error('分析职位URL失败:', error);
      throw error;
    }
  }

  /**
   * 解析职位文本
   */
  async parseJobText(jobText: string, title?: string, company?: string): Promise<{ job: Job; parsing_result: any }> {
    try {
      const response: any = await apiClient.post('/jobs/parse-text', {
        job_text: jobText,
        title,
        company
      });
      return response.data;
    } catch (error) {
      console.error('解析职位文本失败:', error);
      throw error;
    }
  }

  /**
   * 获取职位模板
   */
  async getJobTemplates(): Promise<JobTemplate[]> {
    try {
      const response: any = await apiClient.get('/jobs/templates');
      return response.data.templates;
    } catch (error) {
      console.error('获取职位模板失败:', error);
      throw error;
    }
  }

  /**
   * 职位与简历匹配
   */
  async matchJobWithResume(jobId: number, resumeId?: number): Promise<{
    job: Job;
    resume: any;
    match_result: any;
  }> {
    const response = await apiClient.post(`/jobs/${jobId}/match-resume`, {
      resume_id: resumeId
    });
    return (response as any).data;
  }

  /**
   * 获取职位统计
   */
  async getJobStats(): Promise<JobStats> {
    const response = await apiClient.get('/jobs/stats');
    return (response as any).data;
  }

  /**
   * 搜索职位
   */
  async searchJobs(query: string, filters?: {
    job_type?: string;
    location?: string;
    experience_level?: string;
  }): Promise<JobsResponse> {
    const params = {
      search: query,
      ...filters
    };
    return this.getJobs(params);
  }

  /**
   * 获取推荐职位
   */
  async getRecommendedJobs(limit: number = 10): Promise<Job[]> {
    try {
      const response = await this.getJobs({
        status: 'active',
        per_page: limit
      });
      return response.jobs;
    } catch (error) {
      console.error('获取推荐职位失败:', error);
      return [];
    }
  }

  /**
   * 批量操作职位
   */
  async batchUpdateJobs(jobIds: number[], updates: Partial<CreateJobData>): Promise<void> {
    // 批量更新多个职位
    const promises = jobIds.map(id => this.updateJob(id, updates));
    await Promise.all(promises);
  }

  /**
   * 导出职位数据
   */
  async exportJobs(format: 'json' | 'csv' = 'json'): Promise<Blob> {
    const jobs = await this.getJobs({ per_page: 1000 }); // 获取所有职位
    
    if (format === 'json') {
      const jsonData = JSON.stringify(jobs.jobs, null, 2);
      return new Blob([jsonData], { type: 'application/json' });
    } else {
      // 简单的CSV导出
      const csvHeader = 'Title,Company,Location,Job Type,Created At\n';
      const csvData = jobs.jobs.map(job => 
        `"${job.title}","${job.company}","${job.location}","${job.job_type}","${job.created_at}"`
      ).join('\n');
      
      return new Blob([csvHeader + csvData], { type: 'text/csv' });
    }
  }

  /**
   * 从图片中提取文字 (OCR)
   */
  async extractTextFromImage(imageFile: File): Promise<{ text: string; original_text: string; language: string }> {
    try {
      // 使用专门的文件上传方法，但需要调整参数名
      const formData = new FormData();
      formData.append('image', imageFile);

      const headers: HeadersInit = {};
      const token = localStorage.getItem('access_token');
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 
        (process.env.NODE_ENV === 'production' 
          ? 'https://offerott.com/api/v1'
          : 'http://localhost:5001/api/v1');

      const response = await fetch(`${API_BASE_URL}/jobs/ocr-extract`, {
        method: 'POST',
        headers,
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.message || `HTTP ${response.status}`);
      }

      const result = await response.json();
      return result.data;
    } catch (error) {
      console.error('图片文字识别失败:', error);
      throw error;
    }
  }
}

export const jobService = new JobService(); 