/**
 * 付费和订阅管理服务
 */
import { apiClient as api } from './api';

export interface PricingPlan {
  name: string;
  price: number;
  currency: string;
  period: string;
  features: {
    interviews: number;
    ai_questions: number;
    resume_analysis: number;
    report_history: number;
    voice_interview: boolean;
    custom_questions: boolean;
    advanced_analysis: boolean;
  };
  description: string;
  highlights: string[];
}

export interface Subscription {
  id: number;
  user_id: number;
  plan: string;
  status: string;
  start_date: string;
  end_date?: string;
  monthly_interviews_used: number;
  monthly_ai_questions_used: number;
  monthly_resume_analysis_used: number;
  usage_reset_date: string;
  created_at: string;
  updated_at: string;
}

export interface UsageStats {
  used: number;
  limit: number;
  remaining: number;
}

export interface SubscriptionStatus {
  subscription: Subscription;
  limits: {
    interviews: number;
    ai_questions: number;
    resume_analysis: number;
    report_history: number;
    voice_interview: boolean;
    custom_questions: boolean;
    advanced_analysis: boolean;
  };
  usage: {
    interviews: UsageStats;
    ai_questions: UsageStats;
    resume_analysis: UsageStats;
  };
  features: {
    voice_interview: boolean;
    custom_questions: boolean;
    advanced_analysis: boolean;
  };
  is_expired: boolean;
}

export interface PaymentHistory {
  id: number;
  plan: string;
  amount: number;
  currency: string;
  status: string;
  payment_date: string;
  created_at: string;
}

export interface CheckoutResponse {
  checkout_url: string;
  request_id: string;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string | { message?: string };
  message?: string;
}

class BillingService {
  /**
   * 获取所有付费计划
   */
  async getPlans(): Promise<Record<string, PricingPlan>> {
    try {
      const response = await api.get<ApiResponse<Record<string, PricingPlan>>>('/billing/plans');
      
      if (response.success && response.data) {
        return response.data;
      } else {
        throw new Error(typeof response.error === 'string' ? response.error : (response.error?.message || 'Failed to fetch pricing plans'));
      }
    } catch (error: any) {
      console.error('Error fetching pricing plans:', error);
      throw new Error(error.message || 'Failed to fetch pricing plans');
    }
  }

  /**
   * 获取当前用户的订阅状态
   */
  async getCurrentSubscription(): Promise<SubscriptionStatus> {
    try {
      const response = await api.get<ApiResponse<SubscriptionStatus>>('/billing/subscription');
      
      if (response.success && response.data) {
        return response.data;
      } else {
        throw new Error(typeof response.error === 'string' ? response.error : (response.error?.message || 'Failed to fetch subscription status'));
      }
    } catch (error: any) {
      console.error('Error fetching subscription:', error);
      throw new Error(error.message || 'Failed to fetch subscription status');
    }
  }

  /**
   * 创建支付会话
   */
  async createCheckout(plan: string): Promise<CheckoutResponse> {
    try {
      const response = await api.post<ApiResponse<CheckoutResponse>>('/billing/checkout', { plan });
      
      if (response.success && response.data) {
        return response.data;
      } else {
        throw new Error(typeof response.error === 'string' ? response.error : (response.error?.message || 'Failed to create checkout session'));
      }
    } catch (error: any) {
      console.error('Error creating checkout:', error);
      throw new Error(error.message || 'Failed to create checkout');
    }
  }

  /**
   * 获取使用统计
   */
  async getUsageStats(): Promise<{
    usage: SubscriptionStatus['usage'];
    limits: SubscriptionStatus['limits'];
    features: SubscriptionStatus['features'];
  }> {
    try {
      const response = await api.get<ApiResponse<{
        usage: SubscriptionStatus['usage'];
        limits: SubscriptionStatus['limits'];
        features: SubscriptionStatus['features'];
      }>>('/billing/usage');
      
      if (response.success && response.data) {
        return response.data;
      } else {
        throw new Error(typeof response.error === 'string' ? response.error : (response.error?.message || 'Failed to fetch usage statistics'));
      }
    } catch (error: any) {
      console.error('Error fetching usage stats:', error);
      throw new Error(error.message || 'Failed to fetch usage stats');
    }
  }

  /**
   * 获取支付历史
   */
  async getPaymentHistory(): Promise<PaymentHistory[]> {
    try {
      const response = await api.get<ApiResponse<PaymentHistory[]>>('/billing/history');
      
      if (response.success && response.data) {
        return response.data;
      } else {
        throw new Error(typeof response.error === 'string' ? response.error : (response.error?.message || 'Failed to fetch payment history'));
      }
    } catch (error: any) {
      console.error('Error fetching payment history:', error);
      throw new Error(error.message || 'Failed to fetch payment history');
    }
  }

  /**
   * 取消订阅
   */
  async cancelSubscription(): Promise<void> {
    try {
      const response = await api.post<ApiResponse<null>>('/billing/cancel');
      
      if (!response.success) {
        throw new Error(typeof response.error === 'string' ? response.error : (response.error?.message || 'Failed to cancel subscription'));
      }
    } catch (error: any) {
      console.error('Error cancelling subscription:', error);
      throw new Error(error.message || 'Failed to cancel subscription');
    }
  }

  /**
   * 检查是否可以使用某个功能
   */
  async canUseFeature(feature: string): Promise<boolean> {
    try {
      const subscriptionStatus = await this.getCurrentSubscription();
      
      // 检查订阅是否过期
      if (subscriptionStatus.is_expired) {
        return false;
      }

      // 检查功能权限
      if (feature === 'voice_interview') {
        return subscriptionStatus.features.voice_interview;
      }
      
      if (feature === 'custom_questions') {
        return subscriptionStatus.features.custom_questions;
      }
      
      if (feature === 'advanced_analysis') {
        return subscriptionStatus.features.advanced_analysis;
      }

      // 检查使用次数限制
      if (feature === 'interviews') {
        return subscriptionStatus.usage.interviews.remaining > 0 || subscriptionStatus.usage.interviews.limit === -1;
      }
      
      if (feature === 'ai_questions') {
        return subscriptionStatus.usage.ai_questions.remaining > 0 || subscriptionStatus.usage.ai_questions.limit === -1;
      }
      
      if (feature === 'resume_analysis') {
        return subscriptionStatus.usage.resume_analysis.remaining > 0 || subscriptionStatus.usage.resume_analysis.limit === -1;
      }

      return false;
    } catch (error) {
      console.error('Error checking feature access:', error);
      return false;
    }
  }

  /**
   * 获取升级建议
   */
  getUpgradeSuggestion(currentPlan: string): string | null {
    const suggestions: Record<string, string> = {
      'free': 'basic',
      'basic': 'premium'
    };
    
    return suggestions[currentPlan] || null;
  }

  /**
   * 格式化价格显示
   */
  formatPrice(price: number, currency: string = 'CNY'): string {
    if (price === 0) {
      return '免费';
    }
    
    const currencySymbols: Record<string, string> = {
      'CNY': '¥',
      'USD': '$',
      'EUR': '€'
    };
    
    return `${currencySymbols[currency] || ''}${price}`;
  }

  /**
   * 格式化使用统计显示
   */
  formatUsage(used: number, limit: number): string {
    if (limit === -1) {
      return `${used} / 无限`;
    }
    
    return `${used} / ${limit}`;
  }

  /**
   * 获取计划颜色主题
   */
  getPlanTheme(plan: string): string {
    const themes: Record<string, string> = {
      'free': 'gray',
      'basic': 'blue', 
      'premium': 'purple'
    };
    
    return themes[plan] || 'gray';
  }

  /**
   * 检查是否需要升级提示
   */
  shouldShowUpgradePrompt(subscriptionStatus: SubscriptionStatus): boolean {
    // 如果是免费用户且使用接近限制
    if (subscriptionStatus.subscription.plan === 'free') {
      const interviewUsage = subscriptionStatus.usage.interviews;
      const questionUsage = subscriptionStatus.usage.ai_questions;
      
      // 如果任一功能使用超过80%，提示升级
      if (interviewUsage.limit > 0 && interviewUsage.used / interviewUsage.limit > 0.8) {
        return true;
      }
      
      if (questionUsage.limit > 0 && questionUsage.used / questionUsage.limit > 0.8) {
        return true;
      }
    }
    
    // 如果订阅即将过期（7天内）
    if (subscriptionStatus.subscription.end_date) {
      const endDate = new Date(subscriptionStatus.subscription.end_date);
      const now = new Date();
      const daysUntilExpiry = Math.ceil((endDate.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
      
      if (daysUntilExpiry <= 7 && daysUntilExpiry > 0) {
        return true;
      }
    }
    
    return false;
  }
}

export const billingService = new BillingService();
