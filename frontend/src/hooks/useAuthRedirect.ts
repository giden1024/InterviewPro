import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { authUtils } from '../utils/authUtils';

// 使用认证重定向的Hook
export const useAuthRedirect = () => {
  const navigate = useNavigate();

  useEffect(() => {
    // 设置重定向回调
    authUtils.setRedirectCallback(() => {
      navigate('/login');
    });

    // 清理函数
    return () => {
      authUtils.setRedirectCallback(() => {});
    };
  }, [navigate]);

  // 手动处理API错误的函数
  const handleApiError = (error: any) => {
    authUtils.handleApiError(error);
  };

  return { handleApiError };
}; 