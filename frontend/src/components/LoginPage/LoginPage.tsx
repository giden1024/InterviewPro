import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { LoginPageProps, LoginFormData } from './types';
import logoImg from '../../assets/logo02.png';

const EmailIcon: React.FC<{ className?: string }> = ({ className = "w-6 h-6" }) => (
  <svg className={className} viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
    <path d="M5 0L15 0C18 0 20 1.5 20 5L20 12C20 15.5 18 17 15 17L5 17C2 17 0 15.5 0 12L0 5C0 1.5 2 0 5 0ZM12.34 8.59L15.47 6.09C15.79 5.83 15.84 5.35 15.58 5.03C15.33 4.7 14.85 4.65 14.53 4.91L11.4 7.41C10.64 8.02 9.35 8.02 8.59 7.41L5.46 4.91C5.14 4.65 4.67 4.71 4.41 5.03C4.16 5.35 4.21 5.83 4.53 6.09L7.66 8.59C8.31 9.12 9.16 9.38 10 9.38C10.84 9.38 11.68 9.12 12.34 8.59Z" fill="#68C6F1"/>
  </svg>
);

const LockIcon: React.FC<{ className?: string }> = ({ className = "w-6 h-6" }) => (
  <svg className={className} viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
    <path d="M13.5 6.75L13.5 8.85C13.06 8.79 12.56 8.76 12 8.75L12 6.75C12 3.6 11.11 1.5 6.75 1.5C2.39 1.5 1.5 3.6 1.5 6.75L1.5 8.75C0.94 8.76 0.44 8.79 0 8.85L0 6.75C0 3.85 0.7 0 6.75 0C12.8 0 13.5 3.85 13.5 6.75Z" fill="#68C6F1"/>
    <path d="M16.75 0.1C16.31 0.0400004 15.81 0.01 15.25 0L4.75 0C4.19 0.01 3.69 0.0400004 3.25 0.1C0.7 0.41 0 1.66 0 5L0 7C0 11 1 12 5 12L15 12C19 12 20 11 20 7L20 5C20 1.66 19.3 0.41 16.75 0.1ZM6.71 6.71C6.52 6.89 6.26 7 6 7C5.87 7 5.74 6.97 5.62 6.92C5.49 6.87 5.39 6.8 5.29 6.71C5.11 6.52 5 6.26 5 6C5 5.87 5.03 5.74 5.08 5.62C5.13 5.5 5.2 5.39 5.29 5.29C5.39 5.2 5.49 5.13 5.62 5.08C5.99 4.92 6.43 5.01 6.71 5.29C6.8 5.39 6.87 5.5 6.92 5.62C6.97 5.74 7 5.87 7 6C7 6.26 6.89 6.52 6.71 6.71ZM10.92 6.38C10.87 6.5 10.8 6.61 10.71 6.71C10.52 6.89 10.26 7 10 7C9.73 7 9.48 6.89 9.29 6.71C9.2 6.61 9.13 6.5 9.08 6.38C9.03 6.26 9 6.13 9 6C9 5.73 9.11 5.48 9.29 5.29C9.66 4.92 10.33 4.92 10.71 5.29C10.89 5.48 11 5.73 11 6C11 6.13 10.97 6.26 10.92 6.38ZM14.71 6.71C14.52 6.89 14.26 7 14 7C13.74 7 13.48 6.89 13.29 6.71C13.11 6.52 13 6.27 13 6C13 5.73 13.11 5.48 13.29 5.29C13.67 4.92 14.34 4.92 14.71 5.29C14.75 5.34 14.79 5.39 14.83 5.45C14.87 5.5 14.9 5.56 14.92 5.62C14.95 5.68 14.97 5.74 14.98 5.8C14.99 5.87 15 5.94 15 6C15 6.26 14.89 6.52 14.71 6.71Z" fill="#68C6F1"/>
  </svg>
);

const EyeIcon: React.FC<{ className?: string; isVisible?: boolean }> = ({ className = "w-6 h-6", isVisible = false }) => (
  <svg className={className} viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
    <path d="M10 0C13.56 0 16.94 2.09 19.25 5.72C20.25 7.29 20.25 9.85 19.25 11.41C18.09 13.23 16.67 14.66 15.09 15.64C13.51 16.61 11.78 17.13 10 17.13C6.44 17.13 3.06 15.05 0.75 11.41C-0.25 9.84 -0.25 7.29 0.75 5.72C1.91 3.9 3.33 2.47 4.91 1.49C6.49 0.52 8.22 0 10 0ZM5.96 8.57C5.96 10.8 7.76 12.61 10 12.61C12.24 12.61 14.04 10.8 14.04 8.57C14.04 6.34 12.24 4.53 10 4.53C7.76 4.53 5.96 6.34 5.96 8.57Z" fill="#CCCCCC"/>
    {isVisible && (
      <path d="M2.85 0C1.28 0 0 1.28 0 2.86C0 4.43 1.28 5.71 2.85 5.71C4.42 5.71 5.71 4.43 5.71 2.86C5.71 1.29 4.42 0 2.85 0Z" fill="#CCCCCC" transform="translate(7.15, 5.71)"/>
    )}
  </svg>
);

const GoogleIcon: React.FC<{ className?: string }> = ({ className = "w-[26px] h-[26px]" }) => (
  <svg className={className} viewBox="0 0 26 26" xmlns="http://www.w3.org/2000/svg">
    <rect width="26" height="26" fill="white" rx="5"/>
    <path d="M14.0247 12.5324L0.968062 25.0647C0.356674 24.6483 -0.00628815 23.9555 8.18253e-05 23.2173L8.18253e-05 1.84747C-0.00628815 1.10932 0.356674 0.416509 0.968062 0L14.0247 12.5324Z" fill="#2196F3" transform="translate(0.93, 0)"/>
    <path d="M17.6251 8.58314L13.0565 12.9608L0 0.428314C0.0491398 0.390306 0.10036 0.354956 0.1534 0.322404C0.84344 -0.0944939 1.70534 -0.107945 2.40825 0.287106L17.6251 8.58314Z" fill="#4CAF50" transform="translate(0.97, 0)"/>
    <path d="M10.1053 4.37748C10.1139 5.21071 9.65952 5.98044 8.92476 6.37801L4.56872 8.75497L0 4.37748L4.56872 0L8.92476 2.37696C9.65952 2.7744 10.1139 3.54413 10.1053 4.37748Z" fill="#F0BB1F" transform="translate(14.03, 8.58)"/>
    <path d="M17.6251 4.37749L2.40825 12.6736C1.70378 13.0626 0.845131 13.0491 0.1534 12.6384C0.10036 12.6058 0.0491398 12.5704 0 12.5324L13.0565 0L17.6251 4.37749Z" fill="#F15A2B" transform="translate(0.97, 12.96)"/>
  </svg>
);

const FacebookIcon: React.FC<{ className?: string }> = ({ className = "w-[26px] h-[26px]" }) => (
  <svg className={className} viewBox="0 0 26 26" xmlns="http://www.w3.org/2000/svg">
    <rect width="26" height="26" rx="5" fill="url(#facebookGradient)"/>
    <circle cx="13" cy="13" r="13" fill="url(#facebookGradient)"/>
    <path d="M10.4127 11.4193L10.9902 7.74522L7.37768 7.74522L7.37768 5.36208C7.37768 4.3567 7.88143 3.37615 9.49947 3.37615L11.1429 3.37615L11.1429 0.248244Q9.65203 0 8.22742 0C5.25089 0 3.30729 1.76003 3.30729 4.94498L3.30729 7.74522L0 7.74522L0 11.4193L3.30729 11.4193L3.30729 20.3014C3.97122 20.4032 4.65047 20.4553 5.34244 20.4553C6.03441 20.4553 6.71376 20.4032 7.37768 20.3014L7.37768 11.4193L10.4127 11.4193Z" fill="#FFFFFF" transform="translate(7.43, 5.58)"/>
    <defs>
      <linearGradient id="facebookGradient" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor="#18ACFE"/>
        <stop offset="100%" stopColor="#0163E0"/>
      </linearGradient>
    </defs>
  </svg>
);

export const LoginPage: React.FC<LoginPageProps> = ({
  className,
  theme = 'light',
  onLogin,
  onGoogleLogin,
  onFacebookLogin,
  onForgotPassword,
  onSignUp,
  isLoading: externalIsLoading,
  errorMessage,
  onClearError,
}) => {
  const [formData, setFormData] = useState<LoginFormData>({
    email: '',
    password: '',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [internalIsLoading, setInternalIsLoading] = useState(false);
  const [agreeToPrivacy, setAgreeToPrivacy] = useState(false);
  const navigate = useNavigate();

  // 使用外部传入的loading状态，如果没有则使用内部状态
  const isLoading = externalIsLoading !== undefined ? externalIsLoading : internalIsLoading;

  const handleInputChange = (field: keyof LoginFormData, value: string) => {
    setFormData((prev: LoginFormData) => ({ ...prev, [field]: value }));
    // 当用户开始输入时，清除错误信息
    if (errorMessage && onClearError) {
      onClearError();
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.email || !formData.password || !agreeToPrivacy) return;
    
    setInternalIsLoading(true);
    try {
      await onLogin?.(formData);
    } finally {
      setInternalIsLoading(false);
    }
  };

  const handleSocialLogin = async (provider: 'google' | 'facebook') => {
    setInternalIsLoading(true);
    try {
      if (provider === 'google') {
        await onGoogleLogin?.();
      } else {
        await onFacebookLogin?.();
      }
    } finally {
      setInternalIsLoading(false);
    }
  };

  return (
    <div className={`min-h-screen bg-gradient-to-b from-blue-50 to-blue-200 ${theme === 'dark' ? 'dark' : ''} ${className || ''}`}>
      {/* Background */}
      <div className="absolute inset-0 bg-gradient-to-b from-blue-50 via-blue-100 to-blue-200"></div>
      
      {/* Logo */}
      <div className="absolute top-28 left-1/2 transform -translate-x-1/2 flex items-center space-x-3">
        <img src={logoImg} alt="OfferOtter Logo" className="w-[47px] h-[47px]" />
        <span className="font-bold text-xl text-amber-700" style={{ fontFamily: 'Pump Demi Bold LET' }}>
          Offerotter
        </span>
      </div>

      {/* Login Form Container */}
      <div className="flex items-center justify-center min-h-screen p-4">
        <div className="bg-white rounded-3xl shadow-2xl p-8 w-full max-w-md relative">
          {/* Form Header */}
          <div className="text-center mb-8">
            <h1 className="text-2xl font-medium text-gray-800 mb-2" style={{ fontFamily: 'Poppins' }}>
              Welcome to OfferOtter
            </h1>
            <p className="text-gray-600 text-base leading-relaxed">
              Master Your Dream Job Interview with
              <br />
              AI-Powered Simulation！
            </p>
          </div>

          {/* Error Message Display */}
          {errorMessage && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl">
              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0">
                  <svg className="w-5 h-5 text-red-400 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="flex-1">
                  <p className="text-sm text-red-800 leading-relaxed">
                    {errorMessage}
                  </p>
                </div>
                <button
                  onClick={onClearError}
                  className="flex-shrink-0 text-red-400 hover:text-red-600 transition-colors"
                >
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                  </svg>
                </button>
              </div>
            </div>
          )}

          {/* Login Form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Email Input */}
            <div className="relative">
              <div className="relative bg-white border border-gray-300 rounded-full px-6 py-4 focus-within:border-blue-400 transition-colors">
                <EmailIcon className="absolute left-6 top-1/2 transform -translate-y-1/2 text-blue-400 w-[20px] h-[20px]" />
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => handleInputChange('email', e.target.value)}
                  placeholder="Email address*"
                  className="w-full pl-10 pr-4 text-blue-600 placeholder-blue-400 bg-transparent focus:outline-none"
                  style={{ fontFamily: 'Poppins' }}
                />
              </div>
            </div>

            {/* Password Input */}
            <div className="relative">
              <div className="relative bg-white border border-gray-300 rounded-full px-6 py-4 focus-within:border-blue-400 transition-colors">
                <LockIcon className="absolute left-6 top-1/2 transform -translate-y-1/2 text-blue-400 w-[20px] h-[20px]" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={formData.password}
                  onChange={(e) => handleInputChange('password', e.target.value)}
                  placeholder="Password*"
                  className="w-full pl-10 pr-12 text-blue-600 placeholder-blue-400 bg-transparent focus:outline-none"
                  style={{ fontFamily: 'Poppins' }}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-6 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                  <EyeIcon isVisible={showPassword} className="w-[20px] h-[20px]" />
                </button>
              </div>
            </div>

            {/* Privacy Policy Checkbox */}
            <div className="flex items-start space-x-3">
              <div className="flex items-center h-5">
                <input
                  id="privacy-policy"
                  type="checkbox"
                  checked={agreeToPrivacy}
                  onChange={(e) => setAgreeToPrivacy(e.target.checked)}
                  className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500 focus:ring-2"
                />
              </div>
              <div className="text-sm">
                <label htmlFor="privacy-policy" className="text-gray-700">
                  I have read and agree to the{' '}
                  <button
                    type="button"
                    onClick={() => navigate('/privacy-policy')}
                    className="text-blue-600 hover:text-blue-700 underline font-medium"
                  >
                    Privacy Policy
                  </button>
                  {' '}and{' '}
                  <button
                    type="button"
                    onClick={() => navigate('/terms-of-use')}
                    className="text-blue-600 hover:text-blue-700 underline font-medium"
                  >
                    Terms of Use
                  </button>
                </label>
              </div>
            </div>

            {/* Forgot Password */}
            <div className="text-left">
              <button
                type="button"
                onClick={onForgotPassword}
                className="text-blue-600 font-medium hover:text-blue-700 transition-colors"
                style={{ fontFamily: 'Poppins' }}
              >
                Forgot password?
              </button>
            </div>

            {/* Continue Button */}
            <button
              type="submit"
              disabled={!formData.email || !formData.password || !agreeToPrivacy || isLoading}
              className="w-full bg-gradient-to-r from-blue-300 via-blue-400 to-blue-500 hover:from-blue-400 hover:via-blue-500 hover:to-blue-600 disabled:opacity-50 disabled:cursor-not-allowed text-gray-800 font-medium py-4 rounded-full transition-all duration-200 shadow-lg hover:shadow-xl"
              style={{ fontFamily: 'Poppins', fontSize: '28px' }}
            >
              {isLoading ? 'Loading...' : 'Continue'}
            </button>
            
            {/* Privacy Policy Warning */}
            {(!agreeToPrivacy && (formData.email || formData.password)) && (
              <div className="text-center">
                <p className="text-red-500 text-sm">
                  Please read and agree to the Privacy Policy and Terms of Use
                </p>
              </div>
            )}
          </form>

          {/* Divider - Hidden */}
          <div className="flex items-center my-6" style={{ display: 'none' }}>
            <div className="flex-1 border-t border-gray-300"></div>
            <span className="px-4 text-gray-600 font-medium">OR</span>
            <div className="flex-1 border-t border-gray-300"></div>
          </div>

          {/* Social Login Buttons - Hidden */}
          <div className="space-y-3" style={{ display: 'none' }}>
            <button
              type="button"
              onClick={() => handleSocialLogin('google')}
              disabled={isLoading}
              className="w-full bg-blue-50 hover:bg-blue-100 disabled:opacity-50 disabled:cursor-not-allowed text-gray-800 font-medium py-3 rounded-full transition-all duration-200 flex items-center justify-center space-x-3"
              style={{ fontFamily: 'Poppins' }}
            >
              <GoogleIcon className="w-6 h-6" />
              <span>Continue with Google</span>
            </button>

            <button
              type="button"
              onClick={() => handleSocialLogin('facebook')}
              disabled={isLoading}
              className="w-full bg-blue-50 hover:bg-blue-100 disabled:opacity-50 disabled:cursor-not-allowed text-gray-800 font-medium py-3 rounded-full transition-all duration-200 flex items-center justify-center space-x-3"
              style={{ fontFamily: 'Poppins' }}
            >
              <FacebookIcon className="w-6 h-6" />
              <span>Continue with Facebook</span>
            </button>
          </div>

          {/* Sign Up Link */}
          <div className="text-center mt-6">
            <span className="text-gray-600">Don't have an account? </span>
            <button
              type="button"
              onClick={onSignUp}
              className="text-blue-600 font-medium hover:text-blue-700 transition-colors"
              style={{ fontFamily: 'Poppins' }}
            >
              Sign up
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}; 