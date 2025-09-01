import React, { useState, useEffect } from 'react';
import { Card, Button, Input, Alert, Spin, Progress, Tag, Divider, Space, Row, Col, Statistic, Modal } from 'antd';
import { 
  UserOutlined, 
  LockOutlined, 
  ExperimentOutlined,
  FileTextOutlined,
  MessageOutlined,
  BarChartOutlined,
  SoundOutlined,
  SettingOutlined,
  ReloadOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined
} from '@ant-design/icons';
import { authService } from '../services/authService';
import { billingService } from '../services/billingService';
import { interviewService } from '../services/interviewService';
import { questionService } from '../services/questionService';
import { resumeService } from '../services/resumeService';

interface SubscriptionData {
  subscription: {
    plan: string;
    status: string;
    monthly_interviews_used: number;
    monthly_ai_questions_used: number;
    monthly_resume_analysis_used: number;
  };
  usage: {
    interviews: { used: number; limit: number; remaining: number };
    ai_questions: { used: number; limit: number; remaining: number };
    resume_analysis: { used: number; limit: number; remaining: number };
  };
  features: {
    voice_interview: boolean;
    custom_questions: boolean;
    advanced_analysis: boolean;
  };
}

interface TestResult {
  success: boolean;
  message: string;
  error?: string;
  statusCode?: number;
}

const PermissionTestPage: React.FC = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [loginLoading, setLoginLoading] = useState(false);
  const [email, setEmail] = useState('test@example.com');
  const [password, setPassword] = useState('test123456');
  const [subscriptionData, setSubscriptionData] = useState<SubscriptionData | null>(null);
  const [loading, setLoading] = useState(false);
  const [testResults, setTestResults] = useState<Record<string, TestResult>>({});
  const [testingFunction, setTestingFunction] = useState<string | null>(null);

  // 检查登录状态
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      setIsLoggedIn(true);
      loadSubscriptionData();
    }
  }, []);

  // 登录功能
  const handleLogin = async () => {
    setLoginLoading(true);
    try {
      const result = await authService.login({ email, password });
      if (result.success) {
        setIsLoggedIn(true);
        await loadSubscriptionData();
      } else {
        Modal.error({
          title: '登录失败',
          content: typeof result === 'string' ? result : (result.message || '请检查邮箱和密码')
        });
      }
    } catch (error) {
      Modal.error({
        title: '登录错误',
        content: '网络错误，请稍后重试'
      });
    } finally {
      setLoginLoading(false);
    }
  };

  // 加载订阅数据
  const loadSubscriptionData = async () => {
    setLoading(true);
    try {
      const data = await billingService.getCurrentSubscription();
      setSubscriptionData(data);
    } catch (error) {
      console.error('Failed to load subscription data:', error);
    } finally {
      setLoading(false);
    }
  };

  // 登出功能
  const handleLogout = () => {
    localStorage.removeItem('token');
    setIsLoggedIn(false);
    setSubscriptionData(null);
    setTestResults({});
  };

  // 测试面试创建功能
  const testInterviewCreation = async () => {
    setTestingFunction('interview');
    try {
      // 使用一个假的简历ID进行测试
      const result = await interviewService.createInterview({
        resume_id: 999, // 假的ID，用于触发权限检查
        interview_type: 'comprehensive',
        total_questions: 5
      });
      
      setTestResults(prev => ({
        ...prev,
        interview: {
          success: true,
          message: '面试创建成功！权限检查通过。',
          statusCode: 200
        }
      }));
    } catch (error: any) {
      const statusCode = error.response?.status || 500;
      const message = error.response?.data?.message || error.response?.data?.error || error.message;
      
      setTestResults(prev => ({
        ...prev,
        interview: {
          success: false,
          message: statusCode === 403 ? '权限限制生效：已达使用上限' : 
                   statusCode === 404 ? '通过权限检查，但简历不存在（正常）' :
                   `测试完成：${message}`,
          error: message,
          statusCode
        }
      }));
    } finally {
      setTestingFunction(null);
      await loadSubscriptionData(); // 重新加载使用数据
    }
  };

  // 测试AI问题生成功能
  const testAIQuestionGeneration = async () => {
    setTestingFunction('ai_questions');
    try {
      const result = await questionService.generateQuestions({
        resume_id: 999, // 假的ID
        session_id: 'test-session-123',
        total_questions: 3
      });
      
      setTestResults(prev => ({
        ...prev,
        ai_questions: {
          success: true,
          message: 'AI问题生成成功！权限检查通过。',
          statusCode: 200
        }
      }));
    } catch (error: any) {
      const statusCode = error.response?.status || 500;
      const message = error.response?.data?.message || error.response?.data?.error || error.message;
      
      setTestResults(prev => ({
        ...prev,
        ai_questions: {
          success: false,
          message: statusCode === 403 ? '权限限制生效：已达使用上限' : 
                   statusCode === 404 ? '通过权限检查，但资源不存在（正常）' :
                   `测试完成：${message}`,
          error: message,
          statusCode
        }
      }));
    } finally {
      setTestingFunction(null);
      await loadSubscriptionData();
    }
  };

  // 测试简历分析功能
  const testResumeAnalysis = async () => {
    setTestingFunction('resume_analysis');
    try {
      const result = await resumeService.analyzeResume(999); // 假的ID
      
      setTestResults(prev => ({
        ...prev,
        resume_analysis: {
          success: true,
          message: '简历分析成功！权限检查通过。',
          statusCode: 200
        }
      }));
    } catch (error: any) {
      const statusCode = error.response?.status || 500;
      const message = error.response?.data?.message || error.response?.data?.error || error.message;
      
      setTestResults(prev => ({
        ...prev,
        resume_analysis: {
          success: false,
          message: statusCode === 403 ? '权限限制生效：已达使用上限' : 
                   statusCode === 404 ? '通过权限检查，但简历不存在（正常）' :
                   `测试完成：${message}`,
          error: message,
          statusCode
        }
      }));
    } finally {
      setTestingFunction(null);
      await loadSubscriptionData();
    }
  };

  // 获取计划标签颜色
  const getPlanTagColor = (plan: string) => {
    switch (plan) {
      case 'free': return 'default';
      case 'basic': return 'blue';
      case 'premium': return 'gold';
      default: return 'default';
    }
  };

  // 获取计划中文名
  const getPlanName = (plan: string) => {
    switch (plan) {
      case 'free': return '免费版';
      case 'basic': return '基础版';
      case 'premium': return '高级版';
      default: return plan;
    }
  };

  // 渲染测试结果
  const renderTestResult = (key: string, result: TestResult) => {
    const isSuccess = result.statusCode === 200;
    const isPermissionDenied = result.statusCode === 403;
    const isResourceNotFound = result.statusCode === 404;
    
    let alertType: 'success' | 'error' | 'warning' | 'info' = 'info';
    let icon = <ExperimentOutlined />;
    
    if (isSuccess) {
      alertType = 'success';
      icon = <CheckCircleOutlined />;
    } else if (isPermissionDenied) {
      alertType = 'warning';
      icon = <ExclamationCircleOutlined />;
    } else if (isResourceNotFound) {
      alertType = 'info';
      icon = <CheckCircleOutlined />;
    } else {
      alertType = 'error';
    }

    return (
      <Alert
        key={key}
        type={alertType}
        showIcon
        icon={icon}
        message={result.message}
        description={result.error && `错误详情: ${result.error}`}
        style={{ marginBottom: 8 }}
      />
    );
  };

  // 如果未登录，显示登录界面
  if (!isLoggedIn) {
    return (
      <div style={{ 
        minHeight: '100vh', 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
      }}>
        <Card 
          title={
            <div style={{ textAlign: 'center' }}>
              <ExperimentOutlined style={{ fontSize: 24, marginRight: 8 }} />
              权限功能验证系统
            </div>
          }
          style={{ width: 400, boxShadow: '0 4px 12px rgba(0,0,0,0.15)' }}
        >
          <Space direction="vertical" style={{ width: '100%' }}>
            <Input
              prefix={<UserOutlined />}
              placeholder="邮箱"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              size="large"
            />
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="密码"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              size="large"
              onPressEnter={handleLogin}
            />
            <Button
              type="primary"
              size="large"
              block
              loading={loginLoading}
              onClick={handleLogin}
              icon={<UserOutlined />}
            >
              登录验证系统
            </Button>
            <Alert
              message="测试账号信息"
              description="邮箱: test@example.com | 密码: test123456"
              type="info"
              showIcon
            />
          </Space>
        </Card>
      </div>
    );
  }

  // 主界面
  return (
    <div style={{ padding: 24, background: '#f5f5f5', minHeight: '100vh' }}>
      <div style={{ maxWidth: 1200, margin: '0 auto' }}>
        {/* 页面标题 */}
        <Card style={{ marginBottom: 24 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <h1 style={{ margin: 0, display: 'flex', alignItems: 'center' }}>
                <ExperimentOutlined style={{ marginRight: 8, color: '#1890ff' }} />
                权限功能验证系统
              </h1>
              <p style={{ margin: '8px 0 0 0', color: '#666' }}>
                测试和验证各项功能的权限控制效果
              </p>
            </div>
            <Space>
              <Button icon={<ReloadOutlined />} onClick={loadSubscriptionData} loading={loading}>
                刷新数据
              </Button>
              <Button onClick={handleLogout}>登出</Button>
            </Space>
          </div>
        </Card>

        <Row gutter={24}>
          {/* 左侧：订阅状态和权限信息 */}
          <Col span={12}>
            <Card title="订阅状态" loading={loading} style={{ marginBottom: 24 }}>
              {subscriptionData && (
                <Space direction="vertical" style={{ width: '100%' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span>当前计划:</span>
                    <Tag color={getPlanTagColor(subscriptionData.subscription.plan)} style={{ fontSize: 14 }}>
                      {getPlanName(subscriptionData.subscription.plan)}
                    </Tag>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span>状态:</span>
                    <Tag color="green">{subscriptionData.subscription.status}</Tag>
                  </div>
                </Space>
              )}
            </Card>

            <Card title="使用统计" loading={loading}>
              {subscriptionData && (
                <Space direction="vertical" style={{ width: '100%' }}>
                  {/* 面试次数 */}
                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                      <span><FileTextOutlined /> 面试练习</span>
                      <span>
                        {subscriptionData.usage.interviews.used} / {
                          subscriptionData.usage.interviews.limit === -1 ? '无限' : subscriptionData.usage.interviews.limit
                        }
                      </span>
                    </div>
                    {subscriptionData.usage.interviews.limit !== -1 && (
                      <Progress 
                        percent={Math.round((subscriptionData.usage.interviews.used / subscriptionData.usage.interviews.limit) * 100)}
                        strokeColor="#1890ff"
                      />
                    )}
                  </div>

                  <Divider />

                  {/* AI问题生成 */}
                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                      <span><MessageOutlined /> AI问题生成</span>
                      <span>
                        {subscriptionData.usage.ai_questions.used} / {
                          subscriptionData.usage.ai_questions.limit === -1 ? '无限' : subscriptionData.usage.ai_questions.limit
                        }
                      </span>
                    </div>
                    {subscriptionData.usage.ai_questions.limit !== -1 && (
                      <Progress 
                        percent={Math.round((subscriptionData.usage.ai_questions.used / subscriptionData.usage.ai_questions.limit) * 100)}
                        strokeColor="#52c41a"
                      />
                    )}
                  </div>

                  <Divider />

                  {/* 简历分析 */}
                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                      <span><BarChartOutlined /> 简历分析</span>
                      <span>
                        {subscriptionData.usage.resume_analysis.used} / {
                          subscriptionData.usage.resume_analysis.limit === -1 ? '无限' : subscriptionData.usage.resume_analysis.limit
                        }
                      </span>
                    </div>
                    {subscriptionData.usage.resume_analysis.limit !== -1 && (
                      <Progress 
                        percent={Math.round((subscriptionData.usage.resume_analysis.used / subscriptionData.usage.resume_analysis.limit) * 100)}
                        strokeColor="#faad14"
                      />
                    )}
                  </div>
                </Space>
              )}
            </Card>
          </Col>

          {/* 右侧：功能测试和测试结果 */}
          <Col span={12}>
            <Card title="功能权限" loading={loading} style={{ marginBottom: 24 }}>
              {subscriptionData && (
                <Space direction="vertical" style={{ width: '100%' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span><SoundOutlined /> 语音面试</span>
                    <Tag color={subscriptionData.features.voice_interview ? 'green' : 'default'}>
                      {subscriptionData.features.voice_interview ? '可用' : '不可用'}
                    </Tag>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span><SettingOutlined /> 自定义问题</span>
                    <Tag color={subscriptionData.features.custom_questions ? 'green' : 'default'}>
                      {subscriptionData.features.custom_questions ? '可用' : '不可用'}
                    </Tag>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span><BarChartOutlined /> 高级分析</span>
                    <Tag color={subscriptionData.features.advanced_analysis ? 'green' : 'default'}>
                      {subscriptionData.features.advanced_analysis ? '可用' : '不可用'}
                    </Tag>
                  </div>
                </Space>
              )}
            </Card>

            <Card title="功能测试">
              <Space direction="vertical" style={{ width: '100%' }}>
                <Button
                  type="primary"
                  size="large"
                  block
                  icon={<FileTextOutlined />}
                  loading={testingFunction === 'interview'}
                  onClick={testInterviewCreation}
                >
                  测试面试创建权限
                </Button>
                <Button
                  type="primary"
                  size="large"
                  block
                  icon={<MessageOutlined />}
                  loading={testingFunction === 'ai_questions'}
                  onClick={testAIQuestionGeneration}
                >
                  测试AI问题生成权限
                </Button>
                <Button
                  type="primary"
                  size="large"
                  block
                  icon={<BarChartOutlined />}
                  loading={testingFunction === 'resume_analysis'}
                  onClick={testResumeAnalysis}
                >
                  测试简历分析权限
                </Button>
              </Space>
            </Card>
          </Col>
        </Row>

        {/* 测试结果 */}
        {Object.keys(testResults).length > 0 && (
          <Card title="测试结果" style={{ marginTop: 24 }}>
            {Object.entries(testResults).map(([key, result]) => renderTestResult(key, result))}
          </Card>
        )}

        {/* 使用说明 */}
        <Card title="使用说明" style={{ marginTop: 24 }}>
          <Space direction="vertical" style={{ width: '100%' }}>
            <Alert
              message="权限验证说明"
              description={
                <ul style={{ margin: 0, paddingLeft: 20 }}>
                  <li><strong>绿色成功</strong>：功能执行成功，权限检查通过</li>
                  <li><strong>黄色警告</strong>：权限限制生效，已达使用上限（403错误）</li>
                  <li><strong>蓝色信息</strong>：通过权限检查，但资源不存在（404错误，正常现象）</li>
                  <li><strong>红色错误</strong>：系统错误或其他异常</li>
                </ul>
              }
              type="info"
              showIcon
            />
            <Alert
              message="测试流程"
              description="1. 查看当前订阅状态和使用统计 → 2. 点击测试按钮验证权限 → 3. 观察使用次数变化 → 4. 重复测试直到达到限制"
              type="success"
              showIcon
            />
          </Space>
        </Card>
      </div>
    </div>
  );
};

export default PermissionTestPage;
