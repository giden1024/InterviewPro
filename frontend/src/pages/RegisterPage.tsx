import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUserInfo } from '../hooks/useUserInfo';
import logoImg from '../assets/logo02.png';

const RegisterPage: React.FC = () => {
  const navigate = useNavigate();
  const { registerAndFetchUserInfo, isLoading, error } = useUserInfo();
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    password: '',
    confirmPassword: '',
    agreeToTerms: false
  });
  const [errors, setErrors] = useState<{[key: string]: string}>({});

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const validateForm = () => {
    const newErrors: {[key: string]: string} = {};

    if (!formData.fullName.trim()) {
      newErrors.fullName = 'Full name is required';
    }

    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email';
    }

    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters';
    }

    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }

    if (!formData.agreeToTerms) {
      newErrors.agreeToTerms = 'Please read and agree to the Terms of Use and Privacy Policy';
    }

    return newErrors;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const newErrors = validateForm();
    
    if (Object.keys(newErrors).length === 0) {
      try {
        // Call registration and get user information
        console.log('Registration attempt:', formData);
        
        const response = await registerAndFetchUserInfo(
          formData.email,
          formData.password,
          formData.fullName // Use fullName as username
        );
        
        if (response.success) {
          console.log('Registration successful:', response.data.user);
          // Redirect to home page after successful registration (already auto-logged in)
          navigate('/home');
        }
      } catch (error) {
        console.error('Registration failed:', error);
        // Show error message to user
        alert(error instanceof Error ? error.message : 'Registration failed, please try again');
      }
    } else {
      setErrors(newErrors);
    }
  };

  return (
    <div className="min-h-screen bg-[#EEF9FF]">
      {/* Navigation Bar */}
      <nav className="flex items-center justify-between px-8 py-4 bg-white shadow-sm">
        <div className="flex items-center cursor-pointer" onClick={() => navigate('/')}>
          <img src={logoImg} alt="OfferOtter Logo" className="w-10 h-10 mr-3" />
          <span className="text-xl font-bold text-[#282828]">Offerotter</span>
        </div>
        <div className="flex items-center space-x-6">
          <span className="text-[#3D3D3D]">Already have an account?</span>
          <button
            onClick={() => navigate('/login')}
            className="px-6 py-2 text-[#68C6F1] border border-[#68C6F1] rounded-full hover:bg-[#68C6F1] hover:text-white transition-all"
          >
            Sign In
          </button>
        </div>
      </nav>

      {/* Main Content */}
      <div className="flex items-center justify-center py-12 px-4">
        <div className="max-w-md w-full">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-[#282828] mb-2">Create your account</h1>
            <p className="text-[#3D3D3D]">Join thousands of successful candidates and ace your next interview</p>
          </div>

          {/* Registration Form */}
          <div className="bg-white rounded-2xl shadow-lg p-8">
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Full Name */}
              <div>
                <label htmlFor="fullName" className="block text-sm font-medium text-[#282828] mb-2">
                  Full Name
                </label>
                <input
                  type="text"
                  id="fullName"
                  name="fullName"
                  value={formData.fullName}
                  onChange={handleInputChange}
                  className={`w-full px-4 py-3 border rounded-xl focus:outline-none focus:ring-2 focus:ring-[#68C6F1] focus:border-transparent transition-all ${
                    errors.fullName ? 'border-red-500' : 'border-gray-300'
                  }`}
                  placeholder="Enter your full name"
                />
                {errors.fullName && <p className="text-red-500 text-sm mt-1">{errors.fullName}</p>}
              </div>

              {/* Email */}
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-[#282828] mb-2">
                  Email Address
                </label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  className={`w-full px-4 py-3 border rounded-xl focus:outline-none focus:ring-2 focus:ring-[#68C6F1] focus:border-transparent transition-all ${
                    errors.email ? 'border-red-500' : 'border-gray-300'
                  }`}
                  placeholder="Enter your email"
                />
                {errors.email && <p className="text-red-500 text-sm mt-1">{errors.email}</p>}
              </div>

              {/* Password */}
              <div>
                <label htmlFor="password" className="block text-sm font-medium text-[#282828] mb-2">
                  Password
                </label>
                <input
                  type="password"
                  id="password"
                  name="password"
                  value={formData.password}
                  onChange={handleInputChange}
                  className={`w-full px-4 py-3 border rounded-xl focus:outline-none focus:ring-2 focus:ring-[#68C6F1] focus:border-transparent transition-all ${
                    errors.password ? 'border-red-500' : 'border-gray-300'
                  }`}
                  placeholder="Create a password"
                />
                {errors.password && <p className="text-red-500 text-sm mt-1">{errors.password}</p>}
              </div>

              {/* Confirm Password */}
              <div>
                <label htmlFor="confirmPassword" className="block text-sm font-medium text-[#282828] mb-2">
                  Confirm Password
                </label>
                <input
                  type="password"
                  id="confirmPassword"
                  name="confirmPassword"
                  value={formData.confirmPassword}
                  onChange={handleInputChange}
                  className={`w-full px-4 py-3 border rounded-xl focus:outline-none focus:ring-2 focus:ring-[#68C6F1] focus:border-transparent transition-all ${
                    errors.confirmPassword ? 'border-red-500' : 'border-gray-300'
                  }`}
                  placeholder="Confirm your password"
                />
                {errors.confirmPassword && <p className="text-red-500 text-sm mt-1">{errors.confirmPassword}</p>}
              </div>

              {/* Terms Agreement */}
              <div>
                <label className="flex items-start">
                  <input
                    type="checkbox"
                    name="agreeToTerms"
                    checked={formData.agreeToTerms}
                    onChange={handleInputChange}
                    className="mt-1 mr-3 w-4 h-4 text-[#68C6F1] border-gray-300 rounded focus:ring-[#68C6F1]"
                  />
                  <span className="text-sm text-[#3D3D3D]">
                    I have read and agree to the{' '}
                    <button 
                      type="button" 
                      onClick={() => navigate('/terms-of-use')}
                      className="text-[#68C6F1] hover:underline"
                    >
                      Terms of Use
                    </button>{' '}
                    and{' '}
                    <button 
                      type="button" 
                      onClick={() => navigate('/terms-of-use')}
                      className="text-[#68C6F1] hover:underline"
                    >
                      Privacy Policy
                    </button>
                  </span>
                </label>
                {errors.agreeToTerms && <p className="text-red-500 text-sm mt-1">{errors.agreeToTerms}</p>}
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                className="w-full py-3 bg-gradient-to-r from-[#9CFAFF] to-[#6BBAFF] text-white rounded-xl font-semibold hover:shadow-lg transform hover:scale-105 transition-all"
              >
                Create Account
              </button>
            </form>

            {/* Divider - Hidden */}
            <div className="my-6 flex items-center" style={{ display: 'none' }}>
              <div className="flex-1 border-t border-gray-300"></div>
              <span className="px-4 text-sm text-[#3D3D3D]">Or continue with</span>
              <div className="flex-1 border-t border-gray-300"></div>
            </div>

            {/* Social Login Options - Hidden */}
            <div className="space-y-3" style={{ display: 'none' }}>
              <button
                type="button"
                className="w-full flex items-center justify-center px-4 py-3 border border-gray-300 rounded-xl hover:bg-gray-50 transition-colors"
              >
                <svg className="w-5 h-5 mr-3" viewBox="0 0 24 24">
                  <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                  <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                  <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                  <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                </svg>
                Continue with Google
              </button>

              <button
                type="button"
                className="w-full flex items-center justify-center px-4 py-3 border border-gray-300 rounded-xl hover:bg-gray-50 transition-colors"
              >
                <svg className="w-5 h-5 mr-3" fill="#1877F2" viewBox="0 0 24 24">
                  <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
                </svg>
                Continue with Facebook
              </button>
            </div>
          </div>

          {/* Footer */}
          <div className="text-center mt-6">
            <p className="text-sm text-[#3D3D3D]">
              By signing up, you agree to receive marketing emails from Offerotter.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage; 