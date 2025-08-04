import { useState, useEffect, useCallback } from 'react';
import { interviewService, InterviewSession } from '../services/interviewService';

export interface InterviewRecord {
  id: string;
  title: string;
  date: string;
  duration: string;
  type: 'Mock Interview' | 'Formal interview';
  status: string;
  statusFormatted: { text: string; className: string };
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

  // 格式化时间差为 hh:mm:ss 格式
  const formatDuration = (startTime: string, endTime?: string): string => {
    // 如果没有结束时间，计算从开始时间到现在的时长（进行中的面试）
    const start = new Date(startTime);
    const end = endTime ? new Date(endTime) : new Date();
    const diffMs = Math.max(0, end.getTime() - start.getTime());
    
    const hours = Math.floor(diffMs / 3600000);
    const minutes = Math.floor((diffMs % 3600000) / 60000);
    const seconds = Math.floor((diffMs % 60000) / 1000);
    
    return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
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
    // 处理枚举对象格式 (如 'InterviewType.MOCK')
    const cleanType = type.includes('.') ? type.split('.').pop()?.toLowerCase() : type.toLowerCase();
    
    switch (cleanType) {
      case 'mock':
        return 'Mock Interview';
      case 'technical':
      case 'hr':
      case 'comprehensive':
        return 'Formal interview';
      default:
        return 'Mock Interview';
    }
  };

  // 格式化状态显示
  const formatStatus = (status: string): { text: string; className: string } => {
    switch (status.toLowerCase()) {
      case 'completed':
        return { 
          text: 'Completed', 
          className: 'bg-[#E8F5E8] text-[#2D7738]' 
        };
      case 'in_progress':
        return { 
          text: 'In Progress', 
          className: 'bg-[#FEF3C7] text-[#92400E]' 
        };
      case 'abandoned':
        return { 
          text: 'Abandoned', 
          className: 'bg-[#FEE2E2] text-[#B91C1C]' 
        };
      case 'ready':
        return { 
          text: 'Ready', 
          className: 'bg-[#EEF9FF] text-[#1B5E8C]' 
        };
      case 'created':
        return { 
          text: 'Created', 
          className: 'bg-[#F3F4F6] text-[#6B7280]' 
        };
      default:
        return { 
          text: status, 
          className: 'bg-[#F3F4F6] text-[#6B7280]' 
        };
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
        statusFormatted: formatStatus(session.status),
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
          duration: '01:44:00',
          type: 'Formal interview',
          status: 'completed',
          statusFormatted: formatStatus('completed'),
          session: {} as InterviewSession
        },
        {
          id: 'demo-2',
          title: 'Product Management of TikTok Live',
          date: '2025/04/16',
          duration: '01:44:00',
          type: 'Mock Interview',
          status: 'completed',
          statusFormatted: formatStatus('completed'),
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