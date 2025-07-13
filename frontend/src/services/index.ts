// 导出所有服务
export { apiClient } from './api';
export { authService } from './authService';
export { jobService } from './jobService';
export { resumeService } from './resumeService';
export { interviewService } from './interviewService';
export { analysisService } from './analysisService';
export { questionService } from './questionService';
export { websocketService, interviewWebSocketService } from './websocketService';

// 导出类型定义
export type { User, LoginRequest, RegisterRequest, AuthResponse } from './authService';
export type { Job, JobTemplate, CreateJobData, JobsResponse, JobStats } from './jobService';
export type { Resume, CreateResumeData, ResumeStats, ResumeSearchParams } from './resumeService';
export type { 
  InterviewSession as InterviewSessionType, 
  Question as QuestionType, 
  Answer, 
  CreateInterviewData, 
  SubmitAnswerData, 
  InterviewStats 
} from './interviewService';
export type { AnalysisResult, InterviewReport, UserStatistics } from './analysisService';
export type { 
  Question, 
  InterviewSession, 
  GenerateQuestionsData, 
  QuestionStats 
} from './questionService'; 