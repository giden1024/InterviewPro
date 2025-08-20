// API基础配置
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 
  (process.env.NODE_ENV === 'production' 
    ? 'https://offerott.com/api/v1'
    : 'http://localhost:5001/api/v1');

// 导入认证工具
import { authUtils } from '../utils/authUtils';

// API响应类型
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  error?: {
    code: string;
    message: string;
    details?: any;
  };
}

// HTTP请求配置
class ApiClient {
  private baseURL: string;
  private token: string | null = null;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
    this.token = localStorage.getItem('access_token');
  }

  // 设置认证token
  setToken(token: string) {
    this.token = token;
    localStorage.setItem('access_token', token);
  }

  // 清除token
  clearToken() {
    this.token = null;
    localStorage.removeItem('access_token');
  }

  // 获取请求头
  private getHeaders(): HeadersInit {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    return headers;
  }

  // 处理响应
  private async handleResponse<T>(response: Response): Promise<T> {
    let responseData: any;
    
    try {
      responseData = await response.json();
    } catch (e) {
      // 如果无法解析JSON，创建默认错误响应
      responseData = {
        success: false,
        error: {
          code: 'PARSE_ERROR',
          message: `服务器响应格式错误 (HTTP ${response.status})`
        }
      };
    }

    if (!response.ok) {
      // 从后端响应中提取错误信息（包括401错误）
      let errorMessage = '';
      
      if (responseData.error && responseData.error.message) {
        // 标准的后端错误格式：{ success: false, error: { code: "", message: "" } }
        errorMessage = responseData.error.message;
      } else if (responseData.message) {
        // 兼容旧格式：{ success: false, message: "" }
        errorMessage = responseData.message;
      } else if (typeof responseData === 'string') {
        // 纯字符串错误
        errorMessage = responseData;
      } else {
        // 默认错误信息
        errorMessage = `请求失败 (HTTP ${response.status})`;
      }
      
      // 处理401未授权错误（但仍然要抛出具体的错误信息）
      if (response.status === 401) {
        this.clearToken();
        // 只有在非登录页面时才自动跳转
        if (!window.location.pathname.includes('/login')) {
          authUtils.handle401Error();
        }
        // 抛出具体的错误信息而不是通用的'Unauthorized'
        throw new Error(errorMessage);
      }
      
      // 创建错误对象并抛出
      const error = new Error(errorMessage);
      // 将原始响应数据附加到错误对象上，供调用方使用
      (error as any).response = responseData;
      (error as any).status = response.status;
      
      throw error;
    }

    return responseData;
  }

  // POST请求
  async post<T>(endpoint: string, data?: any): Promise<T> {
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: data ? JSON.stringify(data) : undefined,
    });

    return this.handleResponse<T>(response);
  }

  // GET请求
  async get<T>(endpoint: string): Promise<T> {
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      method: 'GET',
      headers: this.getHeaders(),
    });

    return this.handleResponse<T>(response);
  }

  // PUT请求
  async put<T>(endpoint: string, data?: any): Promise<T> {
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      method: 'PUT',
      headers: this.getHeaders(),
      body: data ? JSON.stringify(data) : undefined,
    });

    return this.handleResponse<T>(response);
  }

  // DELETE请求
  async delete<T>(endpoint: string): Promise<T> {
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      method: 'DELETE',
      headers: this.getHeaders(),
    });

    return this.handleResponse<T>(response);
  }

  // 文件上传请求
  async uploadFile<T>(endpoint: string, file: File, additionalData?: Record<string, string>, fileFieldName: string = 'file'): Promise<T> {
    const formData = new FormData();
    formData.append(fileFieldName, file); // 使用自定义字段名
    
    if (additionalData) {
      Object.entries(additionalData).forEach(([key, value]) => {
        formData.append(key, value);
      });
    }

    const headers: HeadersInit = {};
    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }
    // 不设置 Content-Type，让浏览器自动设置 multipart/form-data 边界

    const response = await fetch(`${this.baseURL}${endpoint}`, {
      method: 'POST',
      headers,
      body: formData,
    });

    return this.handleResponse<T>(response);
  }

  /**
   * 专门用于简化问题生成的文件上传方法
   */
  async uploadResumeForQuestions<T>(endpoint: string, resumeFile: File): Promise<T> {
    return this.uploadFile<T>(endpoint, resumeFile, undefined, 'resume');
  }
}

// 导出API客户端实例
export const apiClient = new ApiClient(API_BASE_URL); 