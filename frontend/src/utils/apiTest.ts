import {
  authService,
  jobService,
  resumeService,
  interviewService,
  analysisService,
  questionService,
  websocketService
} from '../services';

// API测试类
export class ApiTester {
  private testResults: { [key: string]: boolean } = {};

  /**
   * 运行所有API测试
   */
  async runAllTests(): Promise<{ [key: string]: boolean }> {
    console.log('🚀 开始API集成测试...');

    // 测试认证服务
    await this.testAuthService();
    
    // 测试职位服务
    await this.testJobService();
    
    // 测试简历服务
    await this.testResumeService();
    
    // 测试面试服务
    await this.testInterviewService();
    
    // 测试分析服务
    await this.testAnalysisService();
    
    // 测试问题服务
    await this.testQuestionService();
    
    // 测试WebSocket服务
    await this.testWebSocketService();

    console.log('✅ API集成测试完成');
    console.table(this.testResults);
    
    return this.testResults;
  }

  /**
   * 测试认证服务
   */
  private async testAuthService(): Promise<void> {
    console.log('🔐 测试认证服务...');
    
    try {
      // 测试是否已登录检查
      const isAuth = authService.isAuthenticated();
      console.log('- 登录状态检查:', isAuth);
      
      // 如果已登录，测试获取用户信息
      if (isAuth) {
        const userInfo = await authService.getUserInfo();
        console.log('- 用户信息获取:', userInfo);
      }
      
      this.testResults['authService'] = true;
    } catch (error) {
      console.error('❌ 认证服务测试失败:', error);
      this.testResults['authService'] = false;
    }
  }

  /**
   * 测试职位服务
   */
  private async testJobService(): Promise<void> {
    console.log('💼 测试职位服务...');
    
    try {
      // 测试获取职位列表
      const jobs = await jobService.getJobs({ page: 1, per_page: 5 });
      console.log('- 职位列表获取:', jobs.jobs.length);
      
      // 测试获取职位统计
      const stats = await jobService.getJobStats();
      console.log('- 职位统计:', stats);
      
      this.testResults['jobService'] = true;
    } catch (error) {
      console.error('❌ 职位服务测试失败:', error);
      this.testResults['jobService'] = false;
    }
  }

  /**
   * 测试简历服务
   */
  private async testResumeService(): Promise<void> {
    console.log('📄 测试简历服务...');
    
    try {
      // 测试获取简历列表
      const resumes = await resumeService.getResumes({ page: 1, per_page: 5 });
      console.log('- 简历列表获取:', resumes.resumes.length);
      
      // 测试获取简历统计
      const stats = await resumeService.getResumeStats();
      console.log('- 简历统计:', stats);
      
      this.testResults['resumeService'] = true;
    } catch (error) {
      console.error('❌ 简历服务测试失败:', error);
      this.testResults['resumeService'] = false;
    }
  }

  /**
   * 测试面试服务
   */
  private async testInterviewService(): Promise<void> {
    console.log('🎯 测试面试服务...');
    
    try {
      // 测试获取面试列表
      const interviews = await interviewService.getInterviews({ page: 1, per_page: 5 });
      console.log('- 面试列表获取:', interviews.sessions.length);
      
      // 测试获取面试统计
      const stats = await interviewService.getInterviewStats();
      console.log('- 面试统计:', stats);
      
      // 测试获取面试类型
      const types = await interviewService.getInterviewTypes();
      console.log('- 面试类型:', types.length);
      
      this.testResults['interviewService'] = true;
    } catch (error) {
      console.error('❌ 面试服务测试失败:', error);
      this.testResults['interviewService'] = false;
    }
  }

  /**
   * 测试分析服务
   */
  private async testAnalysisService(): Promise<void> {
    console.log('📊 测试分析服务...');
    
    try {
      // 测试获取用户统计
      const stats = await analysisService.getUserStatistics({ days: 30 });
      console.log('- 用户统计:', stats);
      
      this.testResults['analysisService'] = true;
    } catch (error) {
      console.error('❌ 分析服务测试失败:', error);
      this.testResults['analysisService'] = false;
    }
  }

  /**
   * 测试问题服务
   */
  private async testQuestionService(): Promise<void> {
    console.log('❓ 测试问题服务...');
    
    try {
      // 测试获取问题列表
      const questions = await questionService.getQuestions({ page: 1, per_page: 5 });
      console.log('- 问题列表获取:', questions.questions.length);
      
      // 测试获取问题统计
      const stats = await questionService.getQuestionStats();
      console.log('- 问题统计:', stats);
      
      // 测试获取面试会话列表
      const sessions = await questionService.getInterviewSessions({ page: 1, per_page: 5 });
      console.log('- 面试会话列表:', sessions.sessions.length);
      
      this.testResults['questionService'] = true;
    } catch (error) {
      console.error('❌ 问题服务测试失败:', error);
      this.testResults['questionService'] = false;
    }
  }

  /**
   * 测试WebSocket服务
   */
  private async testWebSocketService(): Promise<void> {
    console.log('🔌 测试WebSocket服务...');
    
    try {
      // 测试连接状态
      const isConnected = websocketService.isConnected;
      console.log('- WebSocket连接状态:', isConnected);
      
      // 如果未连接，尝试连接
      if (!isConnected) {
        const token = localStorage.getItem('access_token');
        if (token) {
          await websocketService.connect(token);
          console.log('- WebSocket连接成功');
        }
      }
      
      this.testResults['websocketService'] = true;
    } catch (error) {
      console.error('❌ WebSocket服务测试失败:', error);
      this.testResults['websocketService'] = false;
    }
  }

  /**
   * 测试特定API端点
   */
  async testEndpoint(serviceName: string, methodName: string, ...args: any[]): Promise<any> {
    try {
      let service: any;
      
      switch (serviceName) {
        case 'auth':
          service = authService;
          break;
        case 'job':
          service = jobService;
          break;
        case 'resume':
          service = resumeService;
          break;
        case 'interview':
          service = interviewService;
          break;
        case 'analysis':
          service = analysisService;
          break;
        case 'question':
          service = questionService;
          break;
        default:
          throw new Error(`未知的服务: ${serviceName}`);
      }

      if (typeof service[methodName] !== 'function') {
        throw new Error(`服务 ${serviceName} 中不存在方法 ${methodName}`);
      }

      const result = await service[methodName](...args);
      console.log(`✅ ${serviceName}.${methodName}() 测试成功:`, result);
      return result;
    } catch (error) {
      console.error(`❌ ${serviceName}.${methodName}() 测试失败:`, error);
      throw error;
    }
  }

  /**
   * 生成测试报告
   */
  generateReport(): string {
    const total = Object.keys(this.testResults).length;
    const passed = Object.values(this.testResults).filter(Boolean).length;
    const failed = total - passed;

    return `
📋 API集成测试报告
===================
总测试数: ${total}
通过: ${passed}
失败: ${failed}
成功率: ${((passed / total) * 100).toFixed(2)}%

详细结果:
${Object.entries(this.testResults)
  .map(([service, passed]) => `${passed ? '✅' : '❌'} ${service}`)
  .join('\n')}
    `;
  }
}

// 导出测试实例
export const apiTester = new ApiTester();

// 开发环境下自动暴露到全局对象
if (process.env.NODE_ENV === 'development') {
  (window as any).apiTester = apiTester;
} 