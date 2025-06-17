import React, { useState } from 'react';
import { LoginPageProps, LoginFormData } from './types';

// SVG 图标组件
const LogoIcon: React.FC<{ className?: string }> = ({ className = "w-[116px] h-[47px]" }) => (
  <svg className={className} viewBox="0 0 116 47" xmlns="http://www.w3.org/2000/svg">
    <path d="M1.52543 25.6764Q-1.99439 32.0562 2.60753 36.9396C4.3041 38.7399 6.71666 39.6125 9.14809 40.0681Q25.7136 43.1725 33.6562 39.9113Q40.1334 37.2517 40.7102 31.4015C41.0119 28.3408 39.4807 25.4853 37.7591 22.9368L36.2255 20.6664C35.9253 20.2221 35.9675 19.6447 36.2554 19.1923Q37.8296 16.7188 37.4224 12.0886C36.7751 0.971287 20.1212 -3.14625 11.4118 2.55946Q2.99632 8.07261 5.73413 18.9128C5.85025 19.3726 5.68596 19.8723 5.35069 20.2077Q3.72382 21.8351 1.52543 25.6764Z" fill="#634B41"/>
    <path d="M-0.536443 24.5389Q-4.88558 32.4218 0.89375 38.5546Q3.59757 41.4238 8.71434 42.3827Q25.9641 45.6153 34.5506 42.0897Q42.3379 38.8921 43.0537 31.6325Q43.4894 27.2127 39.7105 21.6186L38.5595 19.9147Q40.1999 16.8659 39.7712 11.9165Q39.1915 2.30175 28.1578 -1.22752Q17.9024 -4.50783 10.1213 0.589663Q0.523824 6.87719 3.31547 18.9299Q1.60383 20.7985 -0.518391 24.5068L-0.536443 24.5389ZM11.4118 2.55946C20.1212 -3.14625 36.7751 0.971287 37.4224 12.0886Q37.8296 16.7188 36.2554 19.1923C35.9675 19.6447 35.9253 20.2221 36.2255 20.6664L37.7591 22.9368C39.4807 25.4853 41.0119 28.3408 40.7102 31.4015Q40.1334 37.2517 33.6562 39.9113Q25.7136 43.1725 9.14809 40.0681C6.71666 39.6125 4.3041 38.7399 2.60753 36.9396Q-1.99439 32.0562 1.52543 25.6764Q3.72382 21.8351 5.35069 20.2077C5.68596 19.8723 5.85025 19.3726 5.73413 18.9128Q2.99632 8.07261 11.4118 2.55946Z" fill="#8FD3F4"/>
  </svg>
);

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
}) => {
  const [formData, setFormData] = useState<LoginFormData>({
    email: '',
    password: '',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handleInputChange = (field: keyof LoginFormData, value: string) => {
    setFormData((prev: LoginFormData) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.email || !formData.password) return;
    
    setIsLoading(true);
    try {
      await onLogin?.(formData);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSocialLogin = async (provider: 'google' | 'facebook') => {
    setIsLoading(true);
    try {
      if (provider === 'google') {
        await onGoogleLogin?.();
      } else {
        await onFacebookLogin?.();
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={`min-h-screen bg-gradient-to-b from-blue-50 to-blue-200 ${theme === 'dark' ? 'dark' : ''} ${className || ''}`}>
      {/* Background */}
      <div className="absolute inset-0 bg-gradient-to-b from-blue-50 via-blue-100 to-blue-200"></div>
      
      {/* Logo */}
      <div className="absolute top-28 left-1/2 transform -translate-x-1/2 flex items-center space-x-3">
        <LogoIcon className="w-[47px] h-[47px]" />
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
              disabled={!formData.email || !formData.password || isLoading}
              className="w-full bg-gradient-to-r from-blue-300 via-blue-400 to-blue-500 hover:from-blue-400 hover:via-blue-500 hover:to-blue-600 disabled:opacity-50 disabled:cursor-not-allowed text-gray-800 font-medium py-4 rounded-full transition-all duration-200 shadow-lg hover:shadow-xl"
              style={{ fontFamily: 'Poppins', fontSize: '28px' }}
            >
              {isLoading ? 'Loading...' : 'Continue'}
            </button>
          </form>

          {/* Divider */}
          <div className="flex items-center my-6">
            <div className="flex-1 border-t border-gray-300"></div>
            <span className="px-4 text-gray-600 font-medium">OR</span>
            <div className="flex-1 border-t border-gray-300"></div>
          </div>

          {/* Social Login Buttons */}
          <div className="space-y-3">
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