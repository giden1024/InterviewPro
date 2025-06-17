import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { User } from '../services/authService';

interface UserState {
  // 状态
  user: User | null;
  isLoading: boolean;
  error: string | null;

  // 操作
  setUser: (user: User) => void;
  clearUser: () => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

export const useUserStore = create<UserState>()(
  persist(
    (set) => ({
      // 初始状态
      user: null,
      isLoading: false,
      error: null,

      // 操作方法
      setUser: (user: User) => set({ user, error: null }),
      clearUser: () => set({ user: null, error: null }),
      setLoading: (isLoading: boolean) => set({ isLoading }),
      setError: (error: string | null) => set({ error }),
    }),
    {
      name: 'user-storage', // localStorage key
      partialize: (state) => ({ user: state.user }), // 只持久化用户信息
    }
  )
); 