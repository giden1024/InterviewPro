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
} 