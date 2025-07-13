import { apiClient } from './api';

// 用户类型
export interface User {
  id: number;
  email: string;
  username?: string;
  avatar_url?: string;
  is_active: boolean;
  created_at: string;
}

// 登录请求类型
export interface LoginRequest {
  email: string;
  password: string;
}

// 注册请求类型
export interface RegisterRequest {
  email: string;
  password: string;
  username?: string;
}

// 认证响应类型
export interface AuthResponse {
  success: boolean;
  data: {
    access_token: string;
    user: User;
  };
  message?: string;
}

// 用户信息响应类型
export interface UserInfoResponse {
  success: boolean;
  data: User;
  message?: string;
}

export class AuthService {
  // 用户登录
  async login(credentials: LoginRequest): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>('/auth/login', credentials);
    
    if (response.success && response.data) {
      // 保存token到API客户端
      apiClient.setToken(response.data.access_token);
    }
    
    return response;
  }

  // 用户注册
  async register(userData: RegisterRequest): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>('/auth/register', userData);
    
    if (response.success && response.data) {
      // 注册成功后自动登录
      apiClient.setToken(response.data.access_token);
    }
    
    return response;
  }

  // 用户登出
  logout(): void {
    apiClient.clearToken();
  }

  // 获取用户信息
  async getUserInfo(): Promise<UserInfoResponse> {
    const response = await apiClient.get<UserInfoResponse>('/auth/profile');
    return response;
  }

  // 检查是否已登录
  isAuthenticated(): boolean {
    const token = localStorage.getItem('access_token');
    if (!token) {
      return false;
    }
    
    // 可以添加更多的token验证逻辑
    // 例如检查token格式、过期时间等
    try {
      // 简单的JWT格式检查
      const parts = token.split('.');
      if (parts.length !== 3) {
        // 不是有效的JWT格式，清除token
        localStorage.removeItem('access_token');
        return false;
      }
      
      return true;
    } catch (error) {
      // token格式错误，清除token
      localStorage.removeItem('access_token');
      return false;
    }
  }
}

// 导出单例实例
export const authService = new AuthService(); 