export interface LoginFormData {
  email: string;
  password: string;
}

export interface LoginPageProps {
  className?: string;
  theme?: 'light' | 'dark';
  onLogin?: (formData: LoginFormData) => Promise<void> | void;
  onGoogleLogin?: () => Promise<void> | void;
  onFacebookLogin?: () => Promise<void> | void;
  onForgotPassword?: () => void;
  onSignUp?: () => void;
  // 新增的错误提示和加载状态属性
  isLoading?: boolean;
  errorMessage?: string;
  onClearError?: () => void;
} 