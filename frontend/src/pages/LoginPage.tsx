import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { LoginPage as LoginComponent } from '../components/LoginPage';
import { LoginFormData } from '../components/LoginPage/types';
import { useUserInfo } from '../hooks/useUserInfo';
import { oauthService } from '../services/oauthService';

const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const { loginAndFetchUserInfo, isLoading } = useUserInfo();
  const [errorMessage, setErrorMessage] = useState<string>('');

  const handleLogin = async (formData: LoginFormData) => {
    try {
      // 清除之前的错误信息
      setErrorMessage('');
      
      // Call login and get user information
      console.log('Login attempt:', formData);
      
      const response = await loginAndFetchUserInfo(formData.email, formData.password);
      
      if (response.success) {
        console.log('Login successful:', response.data.user);
        // Redirect to home page after successful login
        navigate('/home');
      }
    } catch (error) {
      console.error('Login failed:', error);
      
      // 设置友好的错误信息
      let friendlyErrorMessage = '';
      const errorMsg = error instanceof Error ? error.message : 'Login failed, please try again';
      
      if (errorMsg.includes('用户不存在') || errorMsg.includes('用户名不存在') || 
          errorMsg.includes('User not found') || errorMsg.includes('user does not exist')) {
        friendlyErrorMessage = '该邮箱尚未注册，请检查邮箱地址或点击下方"Sign up"注册新账户';
      } else if (errorMsg.includes('密码错误') || errorMsg.includes('密码不正确') || 
                 errorMsg.includes('Incorrect password') || errorMsg.includes('Invalid password') ||
                 errorMsg.includes('password is incorrect')) {
        friendlyErrorMessage = '密码错误，请重新输入正确密码';
      } else if (errorMsg.includes('用户账号已被禁用') || errorMsg.includes('账号被禁用') ||
                 errorMsg.includes('account is disabled') || errorMsg.includes('user is disabled')) {
        friendlyErrorMessage = '您的账户已被禁用，请联系客服处理';
      } else if (errorMsg.includes('网络') || errorMsg.includes('Network') ||
                 errorMsg.includes('fetch')) {
        friendlyErrorMessage = '网络连接异常，请检查网络连接后重试';
      } else if (errorMsg.includes('服务器') || errorMsg.includes('Server') ||
                 errorMsg.includes('Internal Server Error')) {
        friendlyErrorMessage = '服务器暂时不可用，请稍后重试';
      } else {
        friendlyErrorMessage = errorMsg || '登录失败，请重试';
      }
      
      setErrorMessage(friendlyErrorMessage);
    }
  };

  const handleGoogleLogin = async () => {
    try {
      setErrorMessage('');
      console.log('Initiating Google OAuth login...');
      // Redirect to Google OAuth authorization page
      oauthService.initiateGoogleLogin();
    } catch (error) {
      console.error('Google login initiation failed:', error);
      setErrorMessage('Google登录初始化失败，请重试');
    }
  };

  const handleFacebookLogin = async () => {
    try {
      setErrorMessage('');
      console.log('Initiating Facebook OAuth login...');
      // Redirect to Facebook OAuth authorization page
      oauthService.initiateFacebookLogin();
    } catch (error) {
      console.error('Facebook login initiation failed:', error);
      setErrorMessage('Facebook登录初始化失败，请重试');
    }
  };

  const handleForgotPassword = () => {
    // TODO: Redirect to forgot password page
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
      isLoading={isLoading}
      errorMessage={errorMessage}
      onClearError={() => setErrorMessage('')}
    />
  );
};

export default LoginPage; 