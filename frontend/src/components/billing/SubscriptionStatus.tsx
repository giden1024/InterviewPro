/**
 * 订阅状态显示组件
 */
import React, { useState, useEffect } from 'react';
import { billingService, SubscriptionStatus as ISubscriptionStatus } from '../../services/billingService';

interface SubscriptionStatusProps {
  onUpgrade?: () => void;
  showUsageDetails?: boolean;
}

export const SubscriptionStatus: React.FC<SubscriptionStatusProps> = ({
  onUpgrade,
  showUsageDetails = true
}) => {
  const [subscriptionStatus, setSubscriptionStatus] = useState<ISubscriptionStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [cancelling, setCancelling] = useState(false);

  useEffect(() => {
    fetchSubscriptionStatus();
  }, []);

  const fetchSubscriptionStatus = async () => {
    try {
      setLoading(true);
      setError(null);
      const status = await billingService.getCurrentSubscription();
      setSubscriptionStatus(status);
    } catch (error: any) {
      console.error('Failed to fetch subscription status:', error);
      setError(error.message || '获取订阅状态失败');
    } finally {
      setLoading(false);
    }
  };

  const handleCancelSubscription = async () => {
    if (!confirm('确定要取消订阅吗？取消后您将在当前计费周期结束后降级到免费计划。')) {
      return;
    }

    setCancelling(true);
    try {
      await billingService.cancelSubscription();
      alert('订阅已取消。您可以继续使用到当前计费周期结束。');
      await fetchSubscriptionStatus(); // 刷新状态
    } catch (error: any) {
      console.error('Failed to cancel subscription:', error);
      alert(`取消订阅失败: ${error.message}`);
    } finally {
      setCancelling(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'text-green-600 bg-green-100';
      case 'cancelled':
        return 'text-yellow-600 bg-yellow-100';
      case 'expired':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'active':
        return '活跃';
      case 'cancelled':
        return '已取消';
      case 'expired':
        return '已过期';
      default:
        return status;
    }
  };

  const getPlanDisplayName = (plan: string) => {
    const names = {
      'free': '免费版',
      'basic': '基础版',
      'premium': '高级版'
    };
    return names[plan as keyof typeof names] || plan;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('zh-CN');
  };

  const getUsagePercentage = (used: number, limit: number) => {
    if (limit === -1) return 0; // 无限制
    return Math.min((used / limit) * 100, 100);
  };

  const getUsageColor = (percentage: number) => {
    if (percentage >= 90) return 'bg-red-500';
    if (percentage >= 70) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="h-8 bg-gray-200 rounded w-1/2 mb-4"></div>
          <div className="space-y-3">
            <div className="h-4 bg-gray-200 rounded"></div>
            <div className="h-4 bg-gray-200 rounded w-5/6"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="text-center">
          <div className="text-red-600 mb-4">{error}</div>
          <button
            onClick={fetchSubscriptionStatus}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            重试
          </button>
        </div>
      </div>
    );
  }

  if (!subscriptionStatus) {
    return null;
  }

  const { subscription, limits, usage, features, is_expired } = subscriptionStatus;
  const shouldShowUpgrade = billingService.shouldShowUpgradePrompt(subscriptionStatus);

  return (
    <div className="space-y-6">
      {/* 订阅概览 */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-gray-900">订阅状态</h3>
          <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(subscription.status)}`}>
            {getStatusText(subscription.status)}
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <div className="text-sm text-gray-600 mb-1">当前计划</div>
            <div className="text-2xl font-bold text-gray-900 mb-2">
              {getPlanDisplayName(subscription.plan)}
            </div>
            {subscription.plan !== 'free' && (
              <div className="text-sm text-gray-600">
                {subscription.end_date && (
                  <div>到期时间: {formatDate(subscription.end_date)}</div>
                )}
                {subscription.status === 'cancelled' && (
                  <div className="text-yellow-600 mt-1">
                    订阅已取消，将在到期后降级到免费计划
                  </div>
                )}
                {is_expired && (
                  <div className="text-red-600 mt-1">
                    订阅已过期，请续费以继续使用高级功能
                  </div>
                )}
              </div>
            )}
          </div>

          <div className="flex flex-col justify-end">
            {subscription.plan === 'free' ? (
              <button
                onClick={onUpgrade}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                升级计划
              </button>
            ) : subscription.status === 'active' && !is_expired ? (
              <div className="space-y-2">
                <button
                  onClick={onUpgrade}
                  className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  升级计划
                </button>
                <button
                  onClick={handleCancelSubscription}
                  disabled={cancelling}
                  className="w-full px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors disabled:opacity-50"
                >
                  {cancelling ? '处理中...' : '取消订阅'}
                </button>
              </div>
            ) : (
              <button
                onClick={onUpgrade}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
              >
                续费订阅
              </button>
            )}
          </div>
        </div>
      </div>

      {/* 使用统计 */}
      {showUsageDetails && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-6">本月使用情况</h3>
          
          <div className="space-y-6">
            {/* 面试次数 */}
            <div>
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium text-gray-700">面试练习</span>
                <span className="text-sm text-gray-600">
                  {billingService.formatUsage(usage.interviews.used, usage.interviews.limit)}
                </span>
              </div>
              {limits.interviews !== -1 && (
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full transition-all duration-300 ${getUsageColor(getUsagePercentage(usage.interviews.used, usage.interviews.limit))}`}
                    style={{ width: `${getUsagePercentage(usage.interviews.used, usage.interviews.limit)}%` }}
                  ></div>
                </div>
              )}
            </div>

            {/* AI问题生成 */}
            <div>
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium text-gray-700">AI问题生成</span>
                <span className="text-sm text-gray-600">
                  {billingService.formatUsage(usage.ai_questions.used, usage.ai_questions.limit)}
                </span>
              </div>
              {limits.ai_questions !== -1 && (
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full transition-all duration-300 ${getUsageColor(getUsagePercentage(usage.ai_questions.used, usage.ai_questions.limit))}`}
                    style={{ width: `${getUsagePercentage(usage.ai_questions.used, usage.ai_questions.limit)}%` }}
                  ></div>
                </div>
              )}
            </div>

            {/* 简历分析 */}
            <div>
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium text-gray-700">简历分析</span>
                <span className="text-sm text-gray-600">
                  {billingService.formatUsage(usage.resume_analysis.used, usage.resume_analysis.limit)}
                </span>
              </div>
              {limits.resume_analysis !== -1 && (
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full transition-all duration-300 ${getUsageColor(getUsagePercentage(usage.resume_analysis.used, usage.resume_analysis.limit))}`}
                    style={{ width: `${getUsagePercentage(usage.resume_analysis.used, usage.resume_analysis.limit)}%` }}
                  ></div>
                </div>
              )}
            </div>
          </div>

          <div className="mt-6 pt-6 border-t border-gray-200">
            <div className="text-sm text-gray-600">
              使用统计将在每月1日重置
            </div>
          </div>
        </div>
      )}

      {/* 功能权限 */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-6">功能权限</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-700">语音面试</span>
            <span className={`text-sm ${features.voice_interview ? 'text-green-600' : 'text-gray-400'}`}>
              {features.voice_interview ? '✅ 已开通' : '❌ 未开通'}
            </span>
          </div>
          
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-700">自定义问题</span>
            <span className={`text-sm ${features.custom_questions ? 'text-green-600' : 'text-gray-400'}`}>
              {features.custom_questions ? '✅ 已开通' : '❌ 未开通'}
            </span>
          </div>
          
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-700">高级分析报告</span>
            <span className={`text-sm ${features.advanced_analysis ? 'text-green-600' : 'text-gray-400'}`}>
              {features.advanced_analysis ? '✅ 已开通' : '❌ 未开通'}
            </span>
          </div>
          
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-700">历史记录</span>
            <span className="text-sm text-gray-600">
              {limits.report_history === -1 ? '无限制' : `${limits.report_history} 天`}
            </span>
          </div>
        </div>
      </div>

      {/* 升级提示 */}
      {shouldShowUpgrade && (
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <svg className="h-6 w-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div className="ml-3 flex-1">
              <h3 className="text-sm font-medium text-blue-800">
                建议升级
              </h3>
              <div className="mt-1 text-sm text-blue-700">
                {subscription.plan === 'free' 
                  ? '您的使用量接近免费计划限制，升级以获得更多功能和使用额度。'
                  : '您的订阅即将到期，续费以继续享受高级功能。'
                }
              </div>
            </div>
            <div className="ml-3">
              <button
                onClick={onUpgrade}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-blue-700 transition-colors"
              >
                立即升级
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
