import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUserInfo } from '../hooks/useUserInfo';
import { UserInfo } from '../components/UserInfo';

const UserProfilePage: React.FC = () => {
  const navigate = useNavigate();
  const { user, isLoading, error, fetchUserInfo } = useUserInfo();

  useEffect(() => {
    // 页面加载时获取用户信息
    fetchUserInfo();
  }, []);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#EEF9FF] flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-[#68C6F1] border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-[#3D3D3D]">加载用户信息中...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-[#EEF9FF] flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-500 mb-4">❌ {error}</div>
          <button
            onClick={() => navigate('/login')}
            className="px-6 py-2 bg-[#68C6F1] text-white rounded-lg hover:bg-[#5AB5E0] transition-colors"
          >
            重新登录
          </button>
        </div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="min-h-screen bg-[#EEF9FF] flex items-center justify-center">
        <div className="text-center">
          <p className="text-[#3D3D3D] mb-4">请先登录</p>
          <button
            onClick={() => navigate('/login')}
            className="px-6 py-2 bg-[#68C6F1] text-white rounded-lg hover:bg-[#5AB5E0] transition-colors"
          >
            去登录
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#EEF9FF]">
      {/* 导航栏 */}
      <nav className="bg-white shadow-sm px-8 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center cursor-pointer" onClick={() => navigate('/')}>
            <div className="w-10 h-10 bg-gradient-to-r from-[#9CFAFF] to-[#6BBAFF] rounded-full flex items-center justify-center mr-3">
              <span className="text-white font-bold text-lg">O</span>
            </div>
            <span className="text-xl font-bold text-[#282828]">Offerotter</span>
          </div>
          
          <UserInfo showLogout={true} />
        </div>
      </nav>

      {/* 主要内容 */}
      <div className="container mx-auto px-8 py-12">
        <div className="max-w-2xl mx-auto">
          <h1 className="text-3xl font-bold text-[#282828] mb-8">用户信息</h1>
          
          <div className="bg-white rounded-2xl shadow-lg p-8">
            {/* 用户头像和基本信息 */}
            <div className="flex items-center space-x-6 mb-8">
              <div className="w-20 h-20 rounded-full overflow-hidden bg-gradient-to-r from-[#9CFAFF] to-[#6BBAFF] flex items-center justify-center">
                {user.avatar_url ? (
                  <img 
                    src={user.avatar_url} 
                    alt={user.username || user.email}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <span className="text-white font-bold text-2xl">
                    {(user.username || user.email).charAt(0).toUpperCase()}
                  </span>
                )}
              </div>
              
              <div>
                <h2 className="text-2xl font-bold text-[#282828]">
                  {user.username || '用户'}
                </h2>
                <p className="text-[#3D3D3D]">{user.email}</p>
                <p className="text-sm text-[#68C6F1]">
                  用户ID: {user.id}
                </p>
              </div>
            </div>

            {/* 详细信息 */}
            <div className="space-y-4">
              <div className="border-b border-gray-200 pb-4">
                <h3 className="text-lg font-semibold text-[#282828] mb-2">账户信息</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-[#3D3D3D] mb-1">用户名</label>
                    <p className="text-[#282828]">{user.username || '未设置'}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-[#3D3D3D] mb-1">邮箱</label>
                    <p className="text-[#282828]">{user.email}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-[#3D3D3D] mb-1">账户状态</label>
                    <p className={`${user.is_active ? 'text-green-600' : 'text-red-600'}`}>
                      {user.is_active ? '已激活' : '未激活'}
                    </p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-[#3D3D3D] mb-1">注册时间</label>
                    <p className="text-[#282828]">
                      {new Date(user.created_at).toLocaleDateString('zh-CN')}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* 操作按钮 */}
            <div className="flex space-x-4 mt-8">
              <button
                onClick={fetchUserInfo}
                className="px-6 py-2 bg-[#68C6F1] text-white rounded-lg hover:bg-[#5AB5E0] transition-colors"
              >
                刷新信息
              </button>
              <button
                onClick={() => navigate('/home')}
                className="px-6 py-2 border border-[#68C6F1] text-[#68C6F1] rounded-lg hover:bg-[#68C6F1] hover:text-white transition-colors"
              >
                返回主页
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserProfilePage; 