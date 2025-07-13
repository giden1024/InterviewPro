import { authService } from '../services/authService';
import { useUserStore } from '../stores/userStore';

export const useUserInfo = () => {
  const { user, isLoading, error, setUser, setLoading, setError, clearUser } = useUserStore();

  // 获取用户信息
  const fetchUserInfo = async () => {
    if (!authService.isAuthenticated()) {
      clearUser();
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      const response = await authService.getUserInfo();
      
      if (response.success && response.data) {
        setUser(response.data);
      } else {
        throw new Error(response.message || '获取用户信息失败');
      }
    } catch (error) {
      console.error('获取用户信息失败:', error);
      setError(error instanceof Error ? error.message : '获取用户信息失败');
      
      // 如果是认证错误，清除用户信息并重定向到登录页
      if (error instanceof Error && (error.message === 'Unauthorized' || error.message.includes('401'))) {
        clearUser();
        authService.logout();
        // 触发重定向到登录页
        window.location.href = '/login';
      }
    } finally {
      setLoading(false);
    }
  };

  // 登录后获取用户信息
  const loginAndFetchUserInfo = async (email: string, password: string) => {
    try {
      setLoading(true);
      setError(null);

      // 先登录
      const loginResponse = await authService.login({ email, password });
      
      if (loginResponse.success && loginResponse.data) {
        // 登录成功后，设置用户信息（从登录响应中获取）
        setUser(loginResponse.data.user);
        
        // 可选：再次获取最新的用户信息
        await fetchUserInfo();
        
        return loginResponse;
      } else {
        throw new Error(loginResponse.message || '登录失败');
      }
    } catch (error) {
      setError(error instanceof Error ? error.message : '登录失败');
      throw error;
    } finally {
      setLoading(false);
    }
  };

  // 注册后获取用户信息
  const registerAndFetchUserInfo = async (email: string, password: string, username?: string) => {
    try {
      setLoading(true);
      setError(null);

      // 先注册
      const registerResponse = await authService.register({ email, password, username });
      
      if (registerResponse.success && registerResponse.data) {
        // 注册成功后，设置用户信息（从注册响应中获取）
        setUser(registerResponse.data.user);
        
        // 可选：再次获取最新的用户信息
        await fetchUserInfo();
        
        return registerResponse;
      } else {
        throw new Error(registerResponse.message || '注册失败');
      }
    } catch (error) {
      setError(error instanceof Error ? error.message : '注册失败');
      throw error;
    } finally {
      setLoading(false);
    }
  };

  // 登出
  const logout = () => {
    authService.logout();
    clearUser();
  };

  return {
    user,
    isLoading,
    error,
    fetchUserInfo,
    loginAndFetchUserInfo,
    registerAndFetchUserInfo,
    logout,
  };
}; 