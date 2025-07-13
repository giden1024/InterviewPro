// OAuth service for third-party authentication
export class OAuthService {
  // OAuth configuration
  private static readonly GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID || 'your-google-client-id';
  private static readonly FACEBOOK_APP_ID = import.meta.env.VITE_FACEBOOK_APP_ID || 'your-facebook-app-id';
  private static readonly REDIRECT_URI = import.meta.env.VITE_OAUTH_REDIRECT_URI || `${window.location.origin}/auth/callback`;

  /**
   * Initiate Google OAuth login
   */
  static initiateGoogleLogin(): void {
    // 检查是否配置了有效的Google客户端ID
    if (this.GOOGLE_CLIENT_ID === 'your-google-client-id') {
      const errorMessage = `
🔐 Google OAuth 配置错误

Google 客户端ID未配置。请按照以下步骤修复：

1. 创建 frontend/.env.local 文件
2. 添加配置: VITE_GOOGLE_CLIENT_ID=your-actual-google-client-id
3. 从 Google Cloud Console 获取真实的客户端ID

详细步骤请查看: GOOGLE_OAUTH_ERROR_FIX_REPORT.md

或者运行修复脚本: ./fix_google_oauth.sh
      `;
      
      alert(errorMessage);
      console.error('Google OAuth 配置错误: 客户端ID未配置');
      return;
    }

    const scope = 'openid email profile';
    const responseType = 'code';
    const state = this.generateState();
    
    // Store state for validation
    sessionStorage.setItem('oauth_state', state);
    sessionStorage.setItem('oauth_provider', 'google');

    const googleAuthUrl = new URL('https://accounts.google.com/o/oauth2/v2/auth');
    googleAuthUrl.searchParams.append('client_id', this.GOOGLE_CLIENT_ID);
    googleAuthUrl.searchParams.append('redirect_uri', this.REDIRECT_URI);
    googleAuthUrl.searchParams.append('response_type', responseType);
    googleAuthUrl.searchParams.append('scope', scope);
    googleAuthUrl.searchParams.append('state', state);
    googleAuthUrl.searchParams.append('access_type', 'offline');
    googleAuthUrl.searchParams.append('prompt', 'consent');

    console.log('Redirecting to Google OAuth:', googleAuthUrl.toString());
    window.location.href = googleAuthUrl.toString();
  }

  /**
   * Initiate Facebook OAuth login
   */
  static initiateFacebookLogin(): void {
    // 检查是否配置了有效的Facebook应用ID
    if (this.FACEBOOK_APP_ID === 'your-facebook-app-id') {
      const errorMessage = `
🔐 Facebook OAuth 配置错误

Facebook 应用ID未配置。请按照以下步骤修复：

1. 创建 frontend/.env.local 文件
2. 添加配置: VITE_FACEBOOK_APP_ID=your-actual-facebook-app-id
3. 从 Facebook for Developers 获取真实的应用ID

详细步骤请查看: GOOGLE_OAUTH_ERROR_FIX_REPORT.md
      `;
      
      alert(errorMessage);
      console.error('Facebook OAuth 配置错误: 应用ID未配置');
      return;
    }

    const scope = 'email,public_profile';
    const responseType = 'code';
    const state = this.generateState();
    
    // Store state for validation
    sessionStorage.setItem('oauth_state', state);
    sessionStorage.setItem('oauth_provider', 'facebook');

    const facebookAuthUrl = new URL('https://www.facebook.com/v18.0/dialog/oauth');
    facebookAuthUrl.searchParams.append('client_id', this.FACEBOOK_APP_ID);
    facebookAuthUrl.searchParams.append('redirect_uri', this.REDIRECT_URI);
    facebookAuthUrl.searchParams.append('response_type', responseType);
    facebookAuthUrl.searchParams.append('scope', scope);
    facebookAuthUrl.searchParams.append('state', state);

    console.log('Redirecting to Facebook OAuth:', facebookAuthUrl.toString());
    window.location.href = facebookAuthUrl.toString();
  }

  /**
   * Handle OAuth callback from third-party providers
   */
  static async handleCallback(
    code: string, 
    state: string, 
    provider: 'google' | 'facebook'
  ): Promise<{ success: boolean; user?: any; error?: string }> {
    try {
      // Validate state parameter
      const storedState = sessionStorage.getItem('oauth_state');
      const storedProvider = sessionStorage.getItem('oauth_provider');

      if (storedState !== state) {
        throw new Error('Invalid state parameter');
      }

      if (storedProvider !== provider) {
        throw new Error('Provider mismatch');
      }

      // Clean up stored state
      sessionStorage.removeItem('oauth_state');
      sessionStorage.removeItem('oauth_provider');

      // Send authorization code to backend for token exchange
      const response = await fetch('/api/auth/oauth/callback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          code,
          state,
          provider,
          redirect_uri: this.REDIRECT_URI,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'OAuth callback failed');
      }

      const data = await response.json();
      
      // Store access token if provided
      if (data.access_token) {
        localStorage.setItem('access_token', data.access_token);
      }

      return {
        success: true,
        user: data.user,
      };

    } catch (error) {
      console.error('OAuth callback error:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'OAuth callback failed',
      };
    }
  }

  /**
   * Parse OAuth callback URL parameters
   */
  static parseCallbackUrl(url: string = window.location.href): {
    code?: string;
    state?: string;
    error?: string;
    error_description?: string;
  } {
    const urlObj = new URL(url);
    const params = urlObj.searchParams;

    return {
      code: params.get('code') || undefined,
      state: params.get('state') || undefined,
      error: params.get('error') || undefined,
      error_description: params.get('error_description') || undefined,
    };
  }

  /**
   * Generate a random state parameter for OAuth
   */
  private static generateState(): string {
    return Math.random().toString(36).substring(2, 15) + 
           Math.random().toString(36).substring(2, 15);
  }

  /**
   * Check if current page is OAuth callback
   */
  static isOAuthCallback(): boolean {
    const url = new URL(window.location.href);
    return url.pathname === '/auth/callback';
  }

  /**
   * Get OAuth provider from stored session
   */
  static getStoredProvider(): 'google' | 'facebook' | null {
    return sessionStorage.getItem('oauth_provider') as 'google' | 'facebook' | null;
  }
}

// Export singleton instance
export const oauthService = OAuthService; 