/**
 * 付费计划展示组件
 */
import React, { useState, useEffect } from 'react';
import { billingService, PricingPlan } from '../../services/billingService';

interface PricingPlansProps {
  onUpgrade?: (plan: string) => void;
  currentPlan?: string;
  showCurrentPlan?: boolean;
}

export const PricingPlans: React.FC<PricingPlansProps> = ({
  onUpgrade,
  currentPlan = 'free',
  showCurrentPlan = true
}) => {
  const [plans, setPlans] = useState<Record<string, PricingPlan>>({});
  const [loading, setLoading] = useState(true);
  const [upgrading, setUpgrading] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchPlans();
  }, []);

  const fetchPlans = async () => {
    try {
      setLoading(true);
      setError(null);
      const fetchedPlans = await billingService.getPlans();
      setPlans(fetchedPlans);
    } catch (error: any) {
      console.error('Failed to fetch plans:', error);
      setError(error.message || '获取付费计划失败');
    } finally {
      setLoading(false);
    }
  };

  const handleUpgrade = async (planKey: string) => {
    if (planKey === 'free' || planKey === currentPlan) {
      return;
    }

    setUpgrading(planKey);
    try {
      const checkoutData = await billingService.createCheckout(planKey);
      
      // 跳转到支付页面
      window.location.href = checkoutData.checkout_url;
      
      if (onUpgrade) {
        onUpgrade(planKey);
      }
    } catch (error: any) {
      console.error('Failed to create checkout:', error);
      alert(`升级失败: ${error.message}`);
      setUpgrading(null);
    }
  };

  const getPlanTheme = (planKey: string) => {
    const themes = {
      'free': {
        border: 'border-gray-200',
        bg: 'bg-white',
        text: 'text-gray-900',
        button: 'bg-gray-100 text-gray-800 hover:bg-gray-200',
        badge: 'bg-gray-100 text-gray-800'
      },
      'basic': {
        border: 'border-blue-200',
        bg: 'bg-blue-50',
        text: 'text-blue-900',
        button: 'bg-blue-600 text-white hover:bg-blue-700',
        badge: 'bg-blue-100 text-blue-800'
      },
      'premium': {
        border: 'border-purple-200 ring-2 ring-purple-500',
        bg: 'bg-gradient-to-br from-purple-50 to-pink-50',
        text: 'text-purple-900',
        button: 'bg-purple-600 text-white hover:bg-purple-700',
        badge: 'bg-purple-100 text-purple-800'
      }
    };
    
    return themes[planKey as keyof typeof themes] || themes.free;
  };

  const formatFeatureValue = (value: number | boolean, type: string) => {
    if (typeof value === 'boolean') {
      return value ? '✅' : '❌';
    }
    
    if (value === -1) {
      return '无限';
    }
    
    if (type === 'interviews') {
      return `${value} 次/月`;
    }
    
    if (type === 'ai_questions') {
      return `${value} 个/月`;
    }
    
    if (type === 'resume_analysis') {
      return `${value} 次/月`;
    }
    
    if (type === 'report_history') {
      return `${value} 天`;
    }
    
    return value.toString();
  };

  const isCurrentPlan = (planKey: string) => {
    return planKey === currentPlan;
  };

  const canUpgrade = (planKey: string) => {
    const planOrder = ['free', 'basic', 'premium'];
    const currentIndex = planOrder.indexOf(currentPlan);
    const targetIndex = planOrder.indexOf(planKey);
    
    return targetIndex > currentIndex;
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-2 text-gray-600">加载中...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <div className="text-red-600 mb-4">{error}</div>
        <button
          onClick={fetchPlans}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          重试
        </button>
      </div>
    );
  }

  return (
    <div className="py-8">
      <div className="text-center mb-12">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">选择适合您的计划</h2>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
          从免费体验到专业功能，找到最适合您面试准备需求的方案
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto">
        {Object.entries(plans).map(([planKey, plan]) => {
          const theme = getPlanTheme(planKey);
          const isCurrent = isCurrentPlan(planKey);
          const canUpgradeToThis = canUpgrade(planKey);
          
          return (
            <div
              key={planKey}
              className={`relative rounded-2xl ${theme.border} ${theme.bg} p-8 shadow-lg transition-all duration-300 hover:shadow-xl`}
            >
              {/* 推荐标签 */}
              {planKey === 'premium' && (
                <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                  <span className="bg-gradient-to-r from-purple-500 to-pink-500 text-white px-4 py-1 rounded-full text-sm font-medium">
                    推荐
                  </span>
                </div>
              )}

              {/* 当前计划标签 */}
              {isCurrent && showCurrentPlan && (
                <div className="absolute -top-4 right-4">
                  <span className={`${theme.badge} px-3 py-1 rounded-full text-sm font-medium`}>
                    当前计划
                  </span>
                </div>
              )}

              {/* 计划标题和价格 */}
              <div className="text-center mb-8">
                <h3 className={`text-2xl font-bold ${theme.text} mb-2`}>
                  {plan.name}
                </h3>
                <div className="mb-4">
                  <span className={`text-4xl font-bold ${theme.text}`}>
                    {billingService.formatPrice(plan.price, plan.currency)}
                  </span>
                  {plan.price > 0 && (
                    <span className="text-gray-500 ml-1">/{plan.period === 'month' ? '月' : '年'}</span>
                  )}
                </div>
                <p className="text-gray-600">{plan.description}</p>
              </div>

              {/* 功能列表 */}
              <div className="space-y-4 mb-8">
                <div className="grid grid-cols-1 gap-3">
                  {plan.highlights.map((highlight, index) => (
                    <div key={index} className="flex items-center">
                      <svg className="w-5 h-5 text-green-500 mr-3 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                      <span className="text-gray-700">{highlight}</span>
                    </div>
                  ))}
                </div>

                {/* 详细功能对比 */}
                <div className="mt-6 pt-6 border-t border-gray-200">
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div className="text-gray-600">面试次数:</div>
                    <div className="font-medium">{formatFeatureValue(plan.features.interviews, 'interviews')}</div>
                    
                    <div className="text-gray-600">AI问题:</div>
                    <div className="font-medium">{formatFeatureValue(plan.features.ai_questions, 'ai_questions')}</div>
                    
                    <div className="text-gray-600">简历分析:</div>
                    <div className="font-medium">{formatFeatureValue(plan.features.resume_analysis, 'resume_analysis')}</div>
                    
                    <div className="text-gray-600">历史记录:</div>
                    <div className="font-medium">{formatFeatureValue(plan.features.report_history, 'report_history')}</div>
                    
                    <div className="text-gray-600">语音面试:</div>
                    <div className="font-medium">{formatFeatureValue(plan.features.voice_interview, 'feature')}</div>
                    
                    <div className="text-gray-600">自定义问题:</div>
                    <div className="font-medium">{formatFeatureValue(plan.features.custom_questions, 'feature')}</div>
                  </div>
                </div>
              </div>

              {/* 操作按钮 */}
              <div className="text-center">
                {isCurrent ? (
                  <div className={`w-full py-3 px-6 rounded-lg ${theme.badge} font-medium`}>
                    当前计划
                  </div>
                ) : canUpgradeToThis ? (
                  <button
                    onClick={() => handleUpgrade(planKey)}
                    disabled={upgrading === planKey}
                    className={`w-full py-3 px-6 rounded-lg font-medium transition-all duration-200 ${theme.button} disabled:opacity-50 disabled:cursor-not-allowed`}
                  >
                    {upgrading === planKey ? (
                      <div className="flex items-center justify-center">
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-current mr-2"></div>
                        处理中...
                      </div>
                    ) : (
                      `升级到${plan.name}`
                    )}
                  </button>
                ) : planKey === 'free' ? (
                  <div className="w-full py-3 px-6 rounded-lg bg-gray-100 text-gray-600 font-medium">
                    免费使用
                  </div>
                ) : (
                  <div className="w-full py-3 px-6 rounded-lg bg-gray-100 text-gray-600 font-medium">
                    已拥有更高级计划
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* 底部说明 */}
      <div className="text-center mt-12 text-gray-600">
        <p className="mb-2">所有计划都包含基础功能和客户支持</p>
        <p className="text-sm">可随时取消订阅，无长期合约</p>
      </div>
    </div>
  );
};
