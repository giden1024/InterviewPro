import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Card, Result, Button, Spin, Alert } from 'antd';
import { CheckCircleOutlined, LoadingOutlined } from '@ant-design/icons';

const BillingSuccessPage: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [countdown, setCountdown] = useState(5);
  const [processing, setProcessing] = useState(true);

  // 从URL参数获取购买信息
  const requestId = searchParams.get('request_id');
  const checkoutId = searchParams.get('checkout_id');
  const orderId = searchParams.get('order_id');
  const customerId = searchParams.get('customer_id');
  const productId = searchParams.get('product_id');
  
  // 从request_id解析计划信息
  const getPlanFromRequestId = (requestId: string | null): string => {
    if (!requestId) return 'basic';
    const parts = requestId.split('_');
    return parts.length >= 3 ? parts[2] : 'basic';
  };

  const plan = getPlanFromRequestId(requestId);

  useEffect(() => {
    // 模拟处理支付结果
    const processPayment = async () => {
      try {
        console.log('🎯 处理支付成功回调:', {
          requestId,
          checkoutId,
          orderId,
          customerId,
          productId,
          plan
        });

        // 等待2秒模拟处理时间
        await new Promise(resolve => setTimeout(resolve, 2000));
        setProcessing(false);
        
        // 开始倒计时
        const timer = setInterval(() => {
          setCountdown(prev => {
            if (prev <= 1) {
              clearInterval(timer);
              // 跳转回billing页面并传递刷新标识
              navigate('/billing', { 
                replace: true,
                state: { fromSuccess: true, purchasedPlan: plan }
              });
              return 0;
            }
            return prev - 1;
          });
        }, 1000);

        return () => clearInterval(timer);
      } catch (error) {
        console.error('Payment processing error:', error);
        setProcessing(false);
      }
    };

    processPayment();
  }, [navigate, requestId, checkoutId, orderId, customerId, productId, plan]);

  const getPlanName = (plan: string) => {
    switch (plan) {
      case 'basic': return '基础版';
      case 'premium': return '高级版';
      case 'enterprise': return '企业版';
      default: return '订阅计划';
    }
  };

  const getPlanPrice = (plan: string) => {
    switch (plan) {
      case 'basic': return '¥29/月';
      case 'premium': return '¥99/月';
      case 'enterprise': return '¥199/月';
      default: return '';
    }
  };

  const handleGoToBilling = () => {
    navigate('/billing', { 
      replace: true,
      state: { fromSuccess: true, purchasedPlan: plan }
    });
  };

  if (processing) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Card className="w-full max-w-md text-center p-8">
          <Spin 
            indicator={<LoadingOutlined style={{ fontSize: 48, color: '#1890ff' }} spin />}
            className="mb-6"
          />
          <h2 className="text-xl font-semibold mb-2">正在处理支付结果...</h2>
          <p className="text-gray-600">请稍候，我们正在确认您的支付状态并激活订阅权益</p>
          
          {requestId && (
            <div className="mt-4 p-3 bg-blue-50 rounded-lg">
              <p className="text-sm text-blue-600">
                订单号: <span className="font-mono">{requestId}</span>
              </p>
            </div>
          )}
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-2xl">
        <Result
          icon={<CheckCircleOutlined style={{ color: '#52c41a', fontSize: 72 }} />}
          status="success"
          title="🎉 购买成功！"
          subTitle={
            <div className="space-y-4">
              <div className="text-lg">
                <p>恭喜您成功订阅了 <strong className="text-blue-600">{getPlanName(plan)} ({getPlanPrice(plan)})</strong>！</p>
              </div>
              
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <h3 className="font-semibold text-green-800 mb-2">✅ 您的权益已激活</h3>
                <ul className="text-green-700 text-sm space-y-1">
                  {plan === 'basic' && (
                    <>
                      <li>• 面试练习：20次/月 (已重置)</li>
                      <li>• AI问题生成：100次/月 (已重置)</li>
                      <li>• 简历分析：5次/月 (已重置)</li>
                      <li>• ✅ 语音面试功能已开通</li>
                    </>
                  )}
                  {plan === 'premium' && (
                    <>
                      <li>• 面试练习：无限次 (已重置)</li>
                      <li>• AI问题生成：无限次 (已重置)</li>
                      <li>• 简历分析：无限次 (已重置)</li>
                      <li>• ✅ 语音面试功能已开通</li>
                      <li>• ✅ 自定义问题功能已开通</li>
                      <li>• ✅ 高级分析功能已开通</li>
                    </>
                  )}
                </ul>
              </div>
              
              {requestId && (
                <Alert 
                  message={
                    <div>
                      <strong>订单信息</strong>
                      <div className="mt-1 text-sm">
                        <div>订单号: {requestId}</div>
                        {checkoutId && <div>支付ID: {checkoutId}</div>}
                        {orderId && <div>订单ID: {orderId}</div>}
                      </div>
                    </div>
                  }
                  type="info" 
                  showIcon 
                  className="text-left"
                />
              )}
            </div>
          }
          extra={[
            <div key="countdown" className="text-center mb-4">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                <p className="text-blue-700 font-medium">
                  🕒 {countdown} 秒后自动跳转到订阅管理页面
                </p>
                <p className="text-blue-600 text-sm mt-1">
                  您可以在那里查看最新的权益状态
                </p>
              </div>
            </div>,
            <Button 
              key="goto-billing" 
              type="primary" 
              size="large"
              onClick={handleGoToBilling}
              className="px-8"
            >
              立即查看我的订阅
            </Button>
          ]}
        />
      </Card>
    </div>
  );
};

export default BillingSuccessPage;
