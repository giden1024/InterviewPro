/**
 * 付费管理页面
 */
import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { Alert } from 'antd';
import { PricingPlans } from '../components/billing/PricingPlans';
import { SubscriptionStatus } from '../components/billing/SubscriptionStatus';

export const BillingPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'subscription' | 'plans' | 'history'>('subscription');
  const [refreshKey, setRefreshKey] = useState(0);
  const [showSuccessAlert, setShowSuccessAlert] = useState(false);
  const [purchasedPlan, setPurchasedPlan] = useState<string>('');
  const location = useLocation();

  const tabs = [
    { id: 'subscription', name: '订阅状态', icon: '📊' },
    { id: 'plans', name: '付费计划', icon: '💎' },
    { id: 'history', name: '支付历史', icon: '📋' }
  ];

  // 处理从购买成功页面跳转过来的情况
  useEffect(() => {
    const state = location.state as any;
    if (state?.fromSuccess) {
      console.log('🎯 从购买成功页面跳转过来，刷新订阅状态');
      
      // 显示成功提示
      setShowSuccessAlert(true);
      setPurchasedPlan(state.purchasedPlan || '');
      
      // 确保显示订阅状态标签
      setActiveTab('subscription');
      
      // 触发子组件刷新
      setRefreshKey(prev => prev + 1);
      
      // 5秒后隐藏成功提示
      setTimeout(() => {
        setShowSuccessAlert(false);
      }, 5000);
      
      // 清除location state，避免刷新页面时重复处理
      window.history.replaceState({}, document.title);
    }
  }, [location]);

  const handleUpgrade = () => {
    setActiveTab('plans');
  };

  const getPlanName = (plan: string) => {
    switch (plan) {
      case 'basic': return '基础版';
      case 'premium': return '高级版';
      case 'enterprise': return '企业版';
      default: return '订阅计划';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* 购买成功提示 */}
        {showSuccessAlert && (
          <div className="mb-6">
            <Alert
              message="🎉 订阅激活成功！"
              description={`恭喜您成功订阅了${getPlanName(purchasedPlan)}！您的权益已激活，可以立即享受新计划的所有功能。`}
              type="success"
              showIcon
              closable
              onClose={() => setShowSuccessAlert(false)}
              className="shadow-sm"
            />
          </div>
        )}

        {/* 页面标题 */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">订阅管理</h1>
          <p className="text-gray-600">管理您的订阅计划和付费功能</p>
          
          {/* 调试按钮 - 仅开发环境显示 */}
          {process.env.NODE_ENV === 'development' && (
            <div className="mt-4">
              <button
                onClick={() => {
                  console.log('🔍 强制刷新订阅状态');
                  setRefreshKey(prev => prev + 1);
                }}
                className="px-4 py-2 bg-gray-500 text-white rounded text-sm hover:bg-gray-600 mr-2"
              >
                🔄 强制刷新
              </button>
              <button
                onClick={async () => {
                  try {
                    const { billingService } = await import('../services/billingService');
                    const status = await billingService.getCurrentSubscription();
                    console.log('🎯 当前订阅状态:', status);
                    alert(`当前计划: ${status.subscription.plan}\n面试使用: ${status.usage.interviews.used}/${status.usage.interviews.limit}`);
                  } catch (error) {
                    console.error('获取状态失败:', error);
                    alert('获取状态失败: ' + error.message);
                  }
                }}
                className="px-4 py-2 bg-blue-500 text-white rounded text-sm hover:bg-blue-600"
              >
                🔍 调试状态
              </button>
            </div>
          )}
        </div>

        {/* 标签导航 */}
        <div className="flex justify-center mb-8">
          <div className="bg-white rounded-lg shadow-sm p-1">
            <div className="flex space-x-1">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`flex items-center px-4 py-2 rounded-md text-sm font-medium transition-all duration-200 ${
                    activeTab === tab.id
                      ? 'bg-blue-600 text-white shadow-sm'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                  }`}
                >
                  <span className="mr-2">{tab.icon}</span>
                  {tab.name}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* 内容区域 */}
        <div className="max-w-6xl mx-auto">
          {activeTab === 'subscription' && (
            <SubscriptionStatus 
              key={refreshKey} // 添加key强制刷新
              onUpgrade={handleUpgrade}
              showUsageDetails={true}
            />
          )}

          {activeTab === 'plans' && (
            <PricingPlans 
              onUpgrade={() => {
                // 升级成功后可以切换回订阅状态页面
                // setActiveTab('subscription');
              }}
            />
          )}

          {activeTab === 'history' && (
            <PaymentHistorySection />
          )}
        </div>
      </div>
    </div>
  );
};

/**
 * 支付历史组件
 */
const PaymentHistorySection: React.FC = () => {
  const [payments, setPayments] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  React.useEffect(() => {
    fetchPaymentHistory();
  }, []);

  const fetchPaymentHistory = async () => {
    try {
      setLoading(true);
      setError(null);
      const { billingService } = await import('../services/billingService');
      const history = await billingService.getPaymentHistory();
      setPayments(history);
    } catch (error: any) {
      console.error('Failed to fetch payment history:', error);
      setError(error.message || '获取支付历史失败');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-green-600 bg-green-100';
      case 'pending':
        return 'text-yellow-600 bg-yellow-100';
      case 'failed':
        return 'text-red-600 bg-red-100';
      case 'refunded':
        return 'text-gray-600 bg-gray-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'completed':
        return '已完成';
      case 'pending':
        return '处理中';
      case 'failed':
        return '失败';
      case 'refunded':
        return '已退款';
      default:
        return status;
    }
  };

  const getPlanDisplayName = (plan: string) => {
    const names = {
      'basic': '基础版',
      'premium': '高级版'
    };
    return names[plan as keyof typeof names] || plan;
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="animate-pulse space-y-4">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="flex items-center space-x-4">
              <div className="h-4 bg-gray-200 rounded w-1/4"></div>
              <div className="h-4 bg-gray-200 rounded w-1/4"></div>
              <div className="h-4 bg-gray-200 rounded w-1/4"></div>
              <div className="h-4 bg-gray-200 rounded w-1/4"></div>
            </div>
          ))}
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
            onClick={fetchPaymentHistory}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            重试
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="px-6 py-4 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900">支付历史</h3>
      </div>

      {payments.length === 0 ? (
        <div className="px-6 py-12 text-center">
          <div className="text-gray-400 mb-4">
            <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">暂无支付记录</h3>
          <p className="text-gray-600">您还没有任何支付记录</p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  计划
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  金额
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  状态
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  支付时间
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {payments.map((payment) => (
                <tr key={payment.id}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">
                      {getPlanDisplayName(payment.plan)}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">
                      ¥{payment.amount}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(payment.status)}`}>
                      {getStatusText(payment.status)}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(payment.payment_date).toLocaleString('zh-CN')}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
