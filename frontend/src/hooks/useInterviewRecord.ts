import { useState, useEffect, useCallback } from 'react';
import { interviewService, InterviewSession } from '../services/interviewService';

export interface InterviewRecord {
  id: string;
  title: string;
  date: string;
  duration: string;
  type: 'Mock Interview' | 'Formal interview';
  status: string;
  session: InterviewSession;
}

export interface UseInterviewRecordReturn {
  records: InterviewRecord[];
  loading: boolean;
  error: string | null;
  loadRecords: () => Promise<void>;
  deleteRecord: (sessionId: string) => Promise<void>;
  refreshRecords: () => Promise<void>;
}

export const useInterviewRecord = (): UseInterviewRecordReturn => {
  const [records, setRecords] = useState<InterviewRecord[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 格式化时间差为可读格式
  const formatDuration = (startTime: string, endTime?: string): string => {
    if (!endTime) return '未完成';
    
    const start = new Date(startTime);
    const end = new Date(endTime);
    const diffMs = end.getTime() - start.getTime();
    
    const minutes = Math.floor(diffMs / 60000);
    const seconds = Math.floor((diffMs % 60000) / 1000);
    
    if (minutes > 0) {
      return `${minutes}min ${seconds}sec`;
    }
    return `${seconds}sec`;
  };

  // 格式化日期
  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}/${month}/${day}`;
  };

  // 转换面试类型
  const convertInterviewType = (type: string): 'Mock Interview' | 'Formal interview' => {
    switch (type) {
      case 'technical':
        return 'Formal interview';
      case 'hr':
        return 'Formal interview';
      case 'comprehensive':
        return 'Formal interview';
      default:
        return 'Mock Interview';
    }
  };

  // 加载面试记录
  const loadRecords = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await interviewService.getInterviews({
        page: 1,
        per_page: 50 // 获取最近50条记录
      });
      
      const formattedRecords: InterviewRecord[] = response.sessions.map((session) => ({
        id: session.session_id,
        title: session.title || `${session.interview_type} Interview`,
        date: formatDate(session.created_at),
        duration: formatDuration(session.started_at || session.created_at, session.completed_at || undefined),
        type: convertInterviewType(session.interview_type),
        status: session.status,
        session
      }));

      setRecords(formattedRecords);
    } catch (err) {
      console.error('加载面试记录失败:', err);
      setError('加载面试记录失败，请稍后重试');
      
      // 如果API失败，显示演示数据
      setRecords([
        {
          id: 'demo-1',
          title: 'Product Management of TikTok Live',
          date: '2025/04/16',
          duration: '1min 44sec',
          type: 'Formal interview',
          status: 'completed',
          session: {} as InterviewSession
        },
        {
          id: 'demo-2',
          title: 'Product Management of TikTok Live',
          date: '2025/04/16',
          duration: '1min 44sec',
          type: 'Mock Interview',
          status: 'completed',
          session: {} as InterviewSession
        }
      ]);
    } finally {
      setLoading(false);
    }
  }, []);

  // 删除记录
  const deleteRecord = useCallback(async (sessionId: string) => {
    try {
      await interviewService.deleteInterview(sessionId);
      setRecords(prev => prev.filter(record => record.id !== sessionId));
    } catch (err) {
      console.error('删除面试记录失败:', err);
      setError('删除面试记录失败，请稍后重试');
    }
  }, []);

  // 刷新记录
  const refreshRecords = useCallback(async () => {
    await loadRecords();
  }, [loadRecords]);

  // 初始加载
  useEffect(() => {
    loadRecords();
  }, [loadRecords]);

  return {
    records,
    loading,
    error,
    loadRecords,
    deleteRecord,
    refreshRecords
  };
}; 