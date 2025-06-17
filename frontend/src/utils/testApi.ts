import { authService } from '../services/authService';

// 测试API连接的工具函数
export const testApiConnection = async () => {
  try {
    console.log('🧪 开始测试API连接...');
    
    // 测试注册
    const testEmail = `test_${Date.now()}@example.com`;
    const testPassword = 'test123456';
    
    console.log('📝 测试用户注册...');
    const registerResponse = await authService.register({
      email: testEmail,
      password: testPassword,
      username: 'Test User',
    });
    
    if (registerResponse.success) {
      console.log('✅ 注册成功:', registerResponse.data.user);
      
      // 登出
      authService.logout();
      
      // 测试登录
      console.log('🔐 测试用户登录...');
      const loginResponse = await authService.login({
        email: testEmail,
        password: testPassword,
      });
      
      if (loginResponse.success) {
        console.log('✅ 登录成功:', loginResponse.data.user);
        
        // 测试获取用户信息
        console.log('👤 测试获取用户信息...');
        const userInfoResponse = await authService.getUserInfo();
        
        if (userInfoResponse.success) {
          console.log('✅ 获取用户信息成功:', userInfoResponse.data);
          console.log('🎉 API集成测试完成！');
          return true;
        } else {
          console.error('❌ 获取用户信息失败:', userInfoResponse.message);
          return false;
        }
      } else {
        console.error('❌ 登录失败:', loginResponse.message);
        return false;
      }
    } else {
      console.error('❌ 注册失败:', registerResponse.message);
      return false;
    }
  } catch (error) {
    console.error('❌ API测试失败:', error);
    return false;
  }
};

// 在浏览器控制台中可以调用的测试函数
(window as any).testApi = testApiConnection; 