import React from 'react';
import { useUserInfo } from '../hooks/useUserInfo';

interface UserInfoProps {
  className?: string;
  showLogout?: boolean;
}

export const UserInfo: React.FC<UserInfoProps> = ({ 
  className = '', 
  showLogout = true 
}) => {
  const { user, isLoading, error, logout } = useUserInfo();

  if (isLoading) {
    return (
      <div className={`flex items-center space-x-2 ${className}`}>
        <div className="w-8 h-8 bg-gray-200 rounded-full animate-pulse"></div>
        <div className="w-20 h-4 bg-gray-200 rounded animate-pulse"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`text-red-500 text-sm ${className}`}>
        {error}
      </div>
    );
  }

  if (!user) {
    return null;
  }

  return (
    <div className={`flex items-center space-x-3 ${className}`}>
      {/* 用户头像 */}
      <div className="w-8 h-8 rounded-full overflow-hidden bg-gradient-to-r from-[#9CFAFF] to-[#6BBAFF] flex items-center justify-center">
        {user.avatar_url ? (
          <img 
            src={user.avatar_url} 
            alt={user.username || user.email}
            className="w-full h-full object-cover"
          />
        ) : (
          <span className="text-white font-semibold text-sm">
            {(user.username || user.email).charAt(0).toUpperCase()}
          </span>
        )}
      </div>

      {/* 用户信息 */}
      <div className="flex flex-col">
        <span className="text-sm font-medium text-gray-900">
          {user.username || '用户'}
        </span>
        <span className="text-xs text-gray-500">
          {user.email}
        </span>
      </div>

      {/* 登出按钮 */}
      {showLogout && (
        <button
          onClick={logout}
          className="ml-2 px-3 py-1 text-xs text-gray-600 hover:text-red-600 border border-gray-300 hover:border-red-300 rounded-md transition-colors"
        >
          登出
        </button>
      )}
    </div>
  );
}; 