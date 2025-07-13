import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { oauthService } from '../services/oauthService';
import { useUserInfo } from '../hooks/useUserInfo';
import logoImg from '../assets/logo02.png';

const OAuthCallbackPage: React.FC = () => {
  const navigate = useNavigate();
  const { fetchUserInfo } = useUserInfo();
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [error, setError] = useState<string>('');

  useEffect(() => {
    const handleOAuthCallback = async () => {
      try {
        setStatus('loading');

        // Parse callback URL parameters
        const { code, state, error: oauthError, error_description } = oauthService.parseCallbackUrl();

        // Check for OAuth errors from provider
        if (oauthError) {
          const errorMsg = error_description || oauthError || 'OAuth authorization failed';
          throw new Error(errorMsg);
        }

        // Check if we have the required parameters
        if (!code || !state) {
          throw new Error('Missing authorization code or state parameter');
        }

        // Get provider from session storage
        const provider = oauthService.getStoredProvider();
        if (!provider) {
          throw new Error('OAuth provider not found');
        }

        console.log('Processing OAuth callback:', { provider, hasCode: !!code, hasState: !!state });

        // Handle the OAuth callback
        const result = await oauthService.handleCallback(code, state, provider);

        if (!result.success) {
          throw new Error(result.error || 'OAuth callback failed');
        }

        console.log('OAuth login successful:', result.user);

        // Refresh user info after successful OAuth login
        await fetchUserInfo();

        setStatus('success');
        
        // Redirect to home page after successful login
        setTimeout(() => {
          navigate('/home');
        }, 2000);

      } catch (err) {
        console.error('OAuth callback error:', err);
        const errorMessage = err instanceof Error ? err.message : 'OAuth authentication failed';
        setError(errorMessage);
        setStatus('error');

        // Redirect to login page after error
        setTimeout(() => {
          navigate('/login');
        }, 5000);
      }
    };

    // Only process callback if we're on the callback page
    if (oauthService.isOAuthCallback()) {
      handleOAuthCallback();
    } else {
      // If not on callback page, redirect to login
      navigate('/login');
    }
  }, [navigate, fetchUserInfo]);

  const renderContent = () => {
    switch (status) {
      case 'loading':
        return (
          <div className="text-center">
            <div className="w-16 h-16 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
            <h2 className="text-xl font-semibold text-gray-800 mb-2">Processing Login</h2>
            <p className="text-gray-600">Please wait while we complete your authentication...</p>
          </div>
        );

      case 'success':
        return (
          <div className="text-center">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h2 className="text-xl font-semibold text-gray-800 mb-2">Login Successful!</h2>
            <p className="text-gray-600">Redirecting you to the dashboard...</p>
          </div>
        );

      case 'error':
        return (
          <div className="text-center">
            <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
            <h2 className="text-xl font-semibold text-gray-800 mb-2">Login Failed</h2>
            <p className="text-gray-600 mb-4">{error}</p>
            <p className="text-sm text-gray-500">Redirecting you back to login page...</p>
            <button
              onClick={() => navigate('/login')}
              className="mt-4 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Back to Login
            </button>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-blue-200 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-xl p-8 w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <img src={logoImg} alt="OfferOtter Logo" className="w-12 h-12 mx-auto mb-4" />
          <span className="text-xl font-bold text-gray-800">OfferOtter</span>
        </div>

        {/* Content */}
        {renderContent()}
      </div>
    </div>
  );
};

export default OAuthCallbackPage; 