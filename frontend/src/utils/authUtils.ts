// 认证工具函数
export class AuthUtils {
  private static instance: AuthUtils;
  private redirectCallback: (() => void) | null = null;

  static getInstance(): AuthUtils {
    if (!AuthUtils.instance) {
      AuthUtils.instance = new AuthUtils();
    }
    return AuthUtils.instance;
  }

  // 设置重定向回调函数
  setRedirectCallback(callback: () => void) {
    this.redirectCallback = callback;
  }

  // 处理401错误
  handle401Error() {
    // 清除所有认证相关的本地存储
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_info');
    
    // 如果有重定向回调，执行它
    if (this.redirectCallback) {
      this.redirectCallback();
    } else {
      // 如果没有回调，尝试使用window.location重定向
      if (typeof window !== 'undefined' && window.location) {
        window.location.href = '/login';
      }
    }
  }

  // 检查错误是否为401错误
  isUnauthorizedError(error: any): boolean {
    if (!error) return false;
    
    // 检查错误消息
    if (error.message === 'Unauthorized') return true;
    if (error.message && error.message.includes('401')) return true;
    
    // 检查响应状态码
    if (error.status === 401) return true;
    if (error.response && error.response.status === 401) return true;
    
    return false;
  }

  // 统一的错误处理函数
  handleApiError(error: any): void {
    if (this.isUnauthorizedError(error)) {
      console.log('检测到401错误，自动重定向到登录页面');
      this.handle401Error();
    }
  }
}

// 导出单例实例
export const authUtils = AuthUtils.getInstance(); 