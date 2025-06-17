import React from 'react';
import { useNavigate } from 'react-router-dom';
import { LoginPage as LoginComponent } from '../components/LoginPage';
import { LoginFormData } from '../components/LoginPage/types';
import { useUserInfo } from '../hooks/useUserInfo';

const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const { loginAndFetchUserInfo, isLoading, error } = useUserInfo();

  const handleLogin = async (formData: LoginFormData) => {
    try {
      // 调用登录并获取用户信息
      console.log('Login attempt:', formData);
      
      const response = await loginAndFetchUserInfo(formData.email, formData.password);
      
      if (response.success) {
        console.log('Login successful:', response.data.user);
        // 登录成功后跳转到主页
        navigate('/home');
      }
    } catch (error) {
      console.error('Login failed:', error);
      // 显示错误消息给用户
      alert(error instanceof Error ? error.message : '登录失败，请重试');
    }
  };

  const handleGoogleLogin = async () => {
    try {
      // TODO: Google OAuth 登录
      console.log('Google login');
      await new Promise(resolve => setTimeout(resolve, 1000));
      navigate('/dashboard');
    } catch (error) {
      console.error('Google login failed:', error);
    }
  };

  const handleFacebookLogin = async () => {
    try {
      // TODO: Facebook OAuth 登录
      console.log('Facebook login');
      await new Promise(resolve => setTimeout(resolve, 1000));
      navigate('/dashboard');
    } catch (error) {
      console.error('Facebook login failed:', error);
    }
  };

  const handleForgotPassword = () => {
    // TODO: 跳转到忘记密码页面
    console.log('Forgot password');
  };

  const handleSignUp = () => {
    navigate('/register');
  };

  return (
    <LoginComponent
      onLogin={handleLogin}
      onGoogleLogin={handleGoogleLogin}
      onFacebookLogin={handleFacebookLogin}
      onForgotPassword={handleForgotPassword}
      onSignUp={handleSignUp}
    />
  );
};

export default LoginPage; 