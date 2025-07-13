import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { interviewService, InterviewSession } from '../services/interviewService';
import { questionService, Question } from '../services/questionService';
import { aiService, AIAnswerResponse } from '../services/aiService';
import { questionMatchService, HistoricalMatch, QuestionMatchResult } from '../services/questionMatchService';
import { useUserInfo } from '../hooks/useUserInfo';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import logoImg from '../assets/logo02.png';

// 语音识别类型声明
interface ISpeechRecognition extends EventTarget {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  start(): void;
  stop(): void;
  onstart: ((this: ISpeechRecognition, ev: Event) => any) | null;
  onresult: ((this: ISpeechRecognition, ev: SpeechRecognitionEvent) => any) | null;
  onerror: ((this: ISpeechRecognition, ev: SpeechRecognitionErrorEvent) => any) | null;
  onend: ((this: ISpeechRecognition, ev: Event) => any) | null;
}

interface SpeechRecognitionEvent extends Event {
  resultIndex: number;
  results: SpeechRecognitionResultList;
}

interface SpeechRecognitionErrorEvent extends Event {
  error: string;
}

interface SpeechRecognitionResultList {
  length: number;
  item(index: number): SpeechRecognitionResult;
  [index: number]: SpeechRecognitionResult;
}

interface SpeechRecognitionResult {
  length: number;
  item(index: number): SpeechRecognitionAlternative;
  [index: number]: SpeechRecognitionAlternative;
  isFinal: boolean;
}

interface SpeechRecognitionAlternative {
  transcript: string;
  confidence: number;
}

interface FormalInterviewState {
  sessionId?: string;
  jobId?: number;
  resumeId?: number;
}

const FormalInterviewPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user } = useUserInfo();
  
  const state = location.state as FormalInterviewState;
  
  const [session, setSession] = useState<InterviewSession | null>(null);
  const [currentQuestion, setCurrentQuestion] = useState<Question | null>(null);
  const [answer, setAnswer] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [timeRemaining, setTimeRemaining] = useState(3600); // 60 minutes for formal interview
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [autoScroll, setAutoScroll] = useState(true);

  // 屏幕共享相关状态
  const [isScreenSharing, setIsScreenSharing] = useState(false);
  const [screenStream, setScreenStream] = useState<MediaStream | null>(null);
  const [audioStream, setAudioStream] = useState<MediaStream | null>(null);
  const videoRef = useRef<HTMLVideoElement>(null);

  // 语音转录相关状态
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [interimTranscript, setInterimTranscript] = useState('');
  const [transcriptionHistory, setTranscriptionHistory] = useState<Array<{
    id: string;
    text: string;
    timestamp: string;
    confidence: number;
    segmentType: 'sentence' | 'paragraph' | 'pause';
    duration?: number; // 语音持续时间（秒）
  }>>([]);
  const recognitionRef = useRef<ISpeechRecognition | null>(null);
  
  // 分段相关状态
  const [lastSpeechTime, setLastSpeechTime] = useState<number>(0);
  const [currentSegment, setCurrentSegment] = useState<string>('');
  const [segmentStartTime, setSegmentStartTime] = useState<number>(0);
  
  // 语音识别错误管理
  const [noSpeechCount, setNoSpeechCount] = useState<number>(0);
  const [lastNoSpeechTime, setLastNoSpeechTime] = useState<number>(0);
  
  // 语音识别自动重启控制
  const [shouldAutoRestart, setShouldAutoRestart] = useState<boolean>(false);
  const [isManuallyStoppedRef, setIsManuallyStoppedRef] = useState<boolean>(false);

  // 媒体录制相关
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  // AI回答相关状态
  const [aiAnswers, setAiAnswers] = useState<Array<{
    id: string;
    question: string;
    answer: string;
    timestamp: string;
    isGenerating?: boolean;
  }>>([]);
  const [isGeneratingAnswer, setIsGeneratingAnswer] = useState(false);
  const [lastGenerationTime, setLastGenerationTime] = useState<number>(0);

  // 问题匹配相关状态
  const [matchedQuestion, setMatchedQuestion] = useState<HistoricalMatch | null>(null);
  const [isMatching, setIsMatching] = useState(false);
  const [matchError, setMatchError] = useState<string>('');
  const [lastMatchTime, setLastMatchTime] = useState<number>(0);

  // Initialize interview session
  useEffect(() => {
    if (state?.sessionId) {
      loadExistingSession(state.sessionId);
    } else {
      createNewSession();
    }
  }, [state]);

  // Timer countdown
  useEffect(() => {
    if (session && session.status === 'in_progress' && timeRemaining > 0) {
      const timer = setInterval(() => {
        setTimeRemaining(prev => prev - 1);
      }, 1000);
      
      return () => clearInterval(timer);
    }
  }, [session, timeRemaining]);

  // Auto-submit when time runs out
  useEffect(() => {
    if (timeRemaining === 0 && session) {
      handleCompleteInterview();
    }
  }, [timeRemaining, session]);

  // 初始化语音识别
  useEffect(() => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    
    if (SpeechRecognition) {
      const recognition = new SpeechRecognition() as ISpeechRecognition;
      
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = 'en-US';
      
      recognition.onstart = () => {
        console.log('🎤 语音识别开始');
        setIsListening(true);
      };
      
      recognition.onresult = (event) => {
        let finalTranscript = '';
        let interimTranscript = '';
        
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            finalTranscript += transcript;
          } else {
            interimTranscript += transcript;
          }
        }
        
        // 有语音输入时，重置 no-speech 计数
        if (finalTranscript || interimTranscript) {
          setNoSpeechCount(0);
          setLastSpeechTime(Date.now());
        }
        
        if (finalTranscript) {
          const confidence = event.results[event.resultIndex][0].confidence || 0.8;
          processTranscriptSegment(finalTranscript.trim(), confidence);
          console.log('📝 语音转录:', finalTranscript);
        }
        setInterimTranscript(interimTranscript);
      };
      
      recognition.onerror = (event) => {
        console.log(`🔍 语音识别事件: ${event.error}`);
        
        // 对于某些错误，不需要完全停止，可以自动重启
        if (event.error === 'no-speech') {
          console.log('⚠️ 未检测到语音，这是正常的，将自动重试');
          // no-speech是正常现象，不需要特殊处理，让onend处理重启
          return;
        } else if (event.error === 'audio-capture') {
          console.error('❌ 麦克风访问错误:', event.error);
          setError('无法访问麦克风，请检查麦克风权限');
          setIsListening(false);
        } else if (event.error === 'not-allowed') {
          console.error('❌ 麦克风权限被拒绝:', event.error);
          setError('麦克风权限被拒绝，请允许麦克风访问');
          setIsListening(false);
        } else if (event.error === 'network') {
          console.error('❌ 网络错误:', event.error);
          setError('网络错误，语音识别服务不可用');
          setIsListening(false);
        } else {
          console.error('❌ 其他语音识别错误:', event.error);
          setError(`语音识别错误: ${event.error}`);
          setIsListening(false);
        }
      };
      
      recognition.onend = () => {
        console.log('🛑 语音识别结束');
        setIsListening(false);
        setInterimTranscript('');
        
        // 如果应该自动重启且不是手动停止的，则自动重启
        if (shouldAutoRestart && !isManuallyStoppedRef) {
          console.log('🔄 检测到语音识别意外结束，准备自动重启...');
          setTimeout(() => {
            if (shouldAutoRestart && !isManuallyStoppedRef && recognitionRef.current) {
              try {
                console.log('🔄 自动重启语音识别');
                recognitionRef.current.start();
                setIsListening(true);
              } catch (err) {
                console.error('❌ 自动重启语音识别失败:', err);
                // 如果重启失败，等待更长时间再重试
                setTimeout(() => {
                  if (shouldAutoRestart && !isManuallyStoppedRef && recognitionRef.current) {
                    try {
                      console.log('🔄 重试自动重启语音识别');
                      recognitionRef.current.start();
                      setIsListening(true);
                    } catch (retryErr) {
                      console.error('❌ 重试自动重启也失败:', retryErr);
                    }
                  }
                }, 2000);
              }
            }
          }, 1000); // 等待1秒后重启
        } else {
          console.log('🛑 语音识别正常结束，不自动重启');
        }
      };
      
      recognitionRef.current = recognition;
    } else {
      console.warn('⚠️ 浏览器不支持语音识别');
    }
    
    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, []);

  // 页面可见性检测 - 防止页面失去焦点时停止语音识别
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.hidden) {
        console.log('📱 页面失去焦点，但语音识别将继续运行');
        // 不做任何操作，让语音识别继续运行
      } else {
        console.log('📱 页面重新获得焦点');
        // 如果语音识别应该运行但没有运行，尝试重启
        if (shouldAutoRestart && !isListening && !isManuallyStoppedRef && recognitionRef.current) {
          console.log('🔄 页面重新获得焦点，检查语音识别状态并重启');
          setTimeout(() => {
            try {
              recognitionRef.current?.start();
              setIsListening(true);
            } catch (err) {
              console.error('❌ 页面焦点恢复后重启语音识别失败:', err);
            }
          }, 500);
        }
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [shouldAutoRestart, isListening, isManuallyStoppedRef]);

  // 清理媒体流
  useEffect(() => {
    return () => {
      if (screenStream) {
        screenStream.getTracks().forEach(track => track.stop());
      }
      if (audioStream) {
        audioStream.getTracks().forEach(track => track.stop());
      }
    };
  }, [screenStream, audioStream]);

  const loadExistingSession = async (sessionId: string) => {
    try {
      setLoading(true);
      const sessionData = await interviewService.getInterview(sessionId);
      setSession(sessionData.session);
      
      if (sessionData.session.current_question && sessionData.session.current_question > 0) {
        // Load current question from the questions array
        const currentQuestionIndex = sessionData.session.current_question - 1;
        if (sessionData.questions && sessionData.questions[currentQuestionIndex]) {
          setCurrentQuestion(sessionData.questions[currentQuestionIndex] as Question);
        }
      }
    } catch (err) {
      console.error('Failed to load session:', err);
      setError('Failed to load interview session');
    } finally {
      setLoading(false);
    }
  };

  const createNewSession = async () => {
    try {
      setLoading(true);
      const newSession = await interviewService.createInterview({
        resume_id: state?.resumeId || 1,
        interview_type: 'comprehensive', // Use 'comprehensive' instead of 'formal'
        total_questions: 15, // More questions for formal interview
      });
      
      setSession(newSession.session);
      await loadNextQuestion(newSession.session_id);
    } catch (err) {
      console.error('Failed to create session:', err);
      setError('Failed to create interview session');
    } finally {
      setLoading(false);
    }
  };

  const loadNextQuestion = async (sessionId: string) => {
    try {
      const nextQuestion = await interviewService.getNextQuestion(sessionId);
      if ('completed' in nextQuestion && nextQuestion.completed) {
        // Interview is completed
        await handleCompleteInterview();
      } else {
        setCurrentQuestion(nextQuestion as Question);
        setAnswer('');
      }
    } catch (err) {
      console.error('Failed to load next question:', err);
      setError('Failed to load next question');
    }
  };

  const handleSubmitAnswer = async () => {
    if (!session || !currentQuestion || !answer.trim()) return;

    try {
      setLoading(true);
      
      await interviewService.submitAnswer(session.session_id, {
        question_id: currentQuestion.id,
        answer_text: answer.trim(),
        response_time: 3600 - timeRemaining
      });

      // Check if this was the last question
      if ((session.current_question || 0) >= (session.total_questions || 15)) {
        await handleCompleteInterview();
      } else {
        await loadNextQuestion(session.session_id);
      }
    } catch (err) {
      console.error('Failed to submit answer:', err);
      setError('Failed to submit answer');
    } finally {
      setLoading(false);
    }
  };

  const handleCompleteInterview = async () => {
    if (!session) return;

    try {
      await interviewService.endInterview(session.session_id);
      navigate('/complete', { 
        state: { 
          sessionId: session.session_id,
          interviewType: 'formal'
        } 
      });
    } catch (err) {
      console.error('Failed to complete interview:', err);
      setError('Failed to complete interview');
    }
  };

  const handleStartRecording = () => {
    setIsRecording(true);
    console.log('🎤 开始录制音频');
    
    // 同时启动语音识别
    if (!isListening && recognitionRef.current) {
      console.log('🎤 同时启动语音识别功能（带自动重启）');
      toggleSpeechRecognition();
    }
  };

  const handleStopRecording = () => {
    setIsRecording(false);
    console.log('🛑 停止录制音频');
    
    // 同时停止语音识别
    if (isListening && recognitionRef.current) {
      console.log('🛑 同时停止语音识别功能（禁用自动重启）');
      toggleSpeechRecognition();
    }
  };

  // 开始屏幕共享
  const handleStartScreenShare = async () => {
    try {
      console.log('🖥️ 开始请求屏幕共享权限...');
      
      // 请求屏幕共享权限
      const displayStream = await navigator.mediaDevices.getDisplayMedia({
        video: {
          width: { ideal: 1920, max: 1920 },
          height: { ideal: 1080, max: 1080 },
          frameRate: { ideal: 30, max: 60 }
        },
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 44100
        }
      });

      console.log('✅ 屏幕共享权限获取成功');
      setScreenStream(displayStream);
      setIsScreenSharing(true);

      // 将视频流显示到video元素
      if (videoRef.current) {
        videoRef.current.srcObject = displayStream;
      }

      // 分离音频流用于语音识别
      const audioTracks = displayStream.getAudioTracks();
      if (audioTracks.length > 0) {
        const audioOnlyStream = new MediaStream(audioTracks);
        setAudioStream(audioOnlyStream);
        console.log('🔊 检测到音频轨道，开始音频处理');
        
        // 开始录制音频用于转录
        startAudioRecording(audioOnlyStream);
      }

      // 监听屏幕共享结束事件
      displayStream.getVideoTracks()[0].addEventListener('ended', () => {
        console.log('🛑 用户停止了屏幕共享');
        handleStopScreenShare();
      });

    } catch (error) {
      console.error('❌ 屏幕共享失败:', error);
      let errorMessage = '屏幕共享失败';
      
      if (error instanceof Error) {
        if (error.name === 'NotAllowedError') {
          errorMessage = '用户拒绝了屏幕共享权限';
        } else if (error.name === 'NotFoundError') {
          errorMessage = '没有找到可共享的屏幕';
        } else if (error.name === 'NotSupportedError') {
          errorMessage = '浏览器不支持屏幕共享';
        } else {
          errorMessage = `屏幕共享错误: ${error.message}`;
        }
      }
      
      setError(errorMessage);
    }
  };

  // 停止屏幕共享
  const handleStopScreenShare = () => {
    console.log('🛑 停止屏幕共享');
    
    if (screenStream) {
      screenStream.getTracks().forEach(track => {
        track.stop();
        console.log(`🔇 停止轨道: ${track.kind}`);
      });
      setScreenStream(null);
    }
    
    if (audioStream) {
      audioStream.getTracks().forEach(track => track.stop());
      setAudioStream(null);
    }
    
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
    }
    
    setIsScreenSharing(false);
    
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
  };

  // 开始音频录制
  const startAudioRecording = (stream: MediaStream) => {
    try {
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus',
        audioBitsPerSecond: 128000
      });

      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
          console.log('📦 收到音频数据块:', event.data.size, 'bytes');
        }
      };

      mediaRecorder.onstop = () => {
        console.log('🎵 音频录制结束');
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        processAudioForTranscription(audioBlob);
      };

      mediaRecorder.onerror = (event) => {
        console.error('❌ 音频录制错误:', event);
      };

      // 每2秒生成一个数据块，用于实时转录
      mediaRecorder.start(2000);
      mediaRecorderRef.current = mediaRecorder;
      
      console.log('🎤 开始录制音频用于转录');
    } catch (error) {
      console.error('❌ 音频录制初始化失败:', error);
    }
  };

  // 处理音频转录
  const processAudioForTranscription = async (audioBlob: Blob) => {
    try {
      console.log('🔄 开始处理音频转录...');
      
      // 这里可以发送到后端进行更高质量的转录
      // 或者使用Web Speech API进行本地转录
      
      // 示例：发送到后端API
      const formData = new FormData();
      formData.append('audio', audioBlob, 'audio.webm');
      formData.append('session_id', session?.session_id || '');
      
      // 注释掉的后端调用示例
      /*
      const response = await fetch('/api/v1/transcription/process', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: formData
      });
      
      if (response.ok) {
        const result = await response.json();
        console.log('📝 服务器转录结果:', result.transcript);
      }
      */
      
    } catch (error) {
      console.error('❌ 音频转录处理失败:', error);
    }
  };

  // 开始/停止语音识别
  const toggleSpeechRecognition = async () => {
    if (!recognitionRef.current) {
      console.error('⚠️ 语音识别不可用');
      setError('浏览器不支持语音识别功能');
      return;
    }

    if (isListening) {
      console.log('🛑 用户手动停止语音识别');
      setIsManuallyStoppedRef(true); // 标记为手动停止
      setShouldAutoRestart(false); // 禁用自动重启
      try {
        recognitionRef.current.stop();
      } catch (err) {
        console.error('停止语音识别失败:', err);
      }
      setIsListening(false);
    } else {
      // 先检查麦克风权限
      try {
        console.log('🎤 检查麦克风权限...');
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        stream.getTracks().forEach(track => track.stop()); // 立即停止，只是为了检查权限
        console.log('✅ 麦克风权限检查通过');
        
        console.log('🎤 启动语音识别...');
        setTranscript('');
        setInterimTranscript('');
        setError('');
        setIsListening(true); // 先设置状态
        setIsManuallyStoppedRef(false); // 重置手动停止标记
        setShouldAutoRestart(true); // 启用自动重启
        
        try {
          recognitionRef.current.start();
          console.log('✅ 语音识别启动成功，已启用自动重启功能');
        } catch (startErr) {
          console.error('启动语音识别失败:', startErr);
          setIsListening(false);
          setShouldAutoRestart(false);
          setError('启动语音识别失败，请重试');
        }
      } catch (err) {
        console.error('❌ 麦克风权限检查失败:', err);
        const error = err as DOMException;
        if (error.name === 'NotAllowedError') {
          setError('麦克风权限被拒绝，请允许麦克风访问后重试');
        } else if (error.name === 'NotFoundError') {
          setError('未检测到麦克风设备');
        } else {
          setError('无法访问麦克风，请检查设备和权限');
        }
      }
    }
  };

  // 清除转录历史
  const clearTranscriptionHistory = () => {
    setTranscriptionHistory([]);
    setTranscript('');
    setInterimTranscript('');
    setCurrentSegment('');
    setLastSpeechTime(0);
    setSegmentStartTime(0);
    // 清除AI相关状态
    setAiAnswers([]);
    // 重置语音识别错误计数
    setNoSpeechCount(0);
    setLastNoSpeechTime(0);
    console.log('🧹 转录历史和错误状态已清除');
  };

  // AI回答生成函数
  const generateAIAnswer = useCallback(async (question: string) => {
    if (!question.trim() || isGeneratingAnswer) return;
    
    // 防止频繁调用（至少间隔5秒，减少等待时间以支持多问题）
    const now = Date.now();
    if (now - lastGenerationTime < 5000) {
      console.log('AI generation throttled, please wait');
      return;
    }
    
    const answerId = `ai-answer-${now}`;
    
    // 添加生成中的条目
    setAiAnswers(prev => [...prev, {
      id: answerId,
      question: question,
      answer: '',
      timestamp: new Date().toLocaleTimeString(),
      isGenerating: true
    }]);
    
    setIsGeneratingAnswer(true);
    setLastGenerationTime(now);
    
    try {
      console.log('🤖 Generating AI answer for:', question.substring(0, 50) + '...');
      const response = await aiService.generateAnswer(question);
      
      // 更新对应的答案
      setAiAnswers(prev => prev.map(item => 
        item.id === answerId 
          ? { ...item, answer: response.answer, isGenerating: false }
          : item
      ));
      
      console.log('✅ AI answer generated successfully');
    } catch (error) {
      console.error('Failed to generate AI answer:', error);
      
      // 更新为错误状态
      setAiAnswers(prev => prev.map(item => 
        item.id === answerId 
          ? { ...item, answer: 'Unable to generate answer at this time. Please try again later.', isGenerating: false }
          : item
      ));
    } finally {
      setIsGeneratingAnswer(false);
    }
  }, [isGeneratingAnswer, lastGenerationTime]);

  // 问题检测函数
  const shouldGenerateAnswer = useCallback((text: string): boolean => {
    // 基本条件检查
    if (text.length < 10) return false;
    
    const textLower = text.toLowerCase().trim();
    
    // 检查是否包含问号
    if (textLower.includes('?')) return true;
    
    // 检查是否包含疑问词
    const questionWords = ['how', 'what', 'why', 'when', 'where', 'who', 'tell', 'describe', 'explain', 'can you', 'would you', 'do you'];
    const hasQuestionWord = questionWords.some(word => textLower.includes(word));
    
    // 如果包含疑问词，就认为是问题（不强制要求标点符号）
    if (hasQuestionWord) {
      console.log(`🔍 检测到疑问词: ${questionWords.find(word => textLower.includes(word))}`);
      return true;
    }
    
    // 检查是否以句号或问号结尾（完整句子）
    const isCompleteSentence = textLower.endsWith('.') || textLower.endsWith('?');
    
    return isCompleteSentence;
  }, []);

  // 重新生成AI回答（针对最新的问题）
  const regenerateAIAnswer = useCallback(() => {
    const lastAnswer = aiAnswers[aiAnswers.length - 1];
    if (lastAnswer) {
      setLastGenerationTime(0); // 重置时间限制
      generateAIAnswer(lastAnswer.question);
    }
  }, [aiAnswers, generateAIAnswer]);
  
  // 清除所有AI答案
  const clearAIAnswers = useCallback(() => {
    setAiAnswers([]);
  }, []);

  // 处理问题匹配
  const handleQuestionMatch = useCallback(async (speechText: string) => {
    const now = Date.now();
    
    // 防抖：如果距离上次匹配不到3秒，跳过
    if (now - lastMatchTime < 3000) {
      console.log('🔄 防抖：跳过问题匹配');
      return;
    }
    
    setLastMatchTime(now);
    setIsMatching(true);
    setMatchError('');
    
    try {
      console.log('🔍 开始匹配历史问题:', speechText);
      
      const result = await questionMatchService.matchHistoricalQuestion({
        speech_text: speechText,
        limit: 1 // 只取最匹配的一个
      });
      
      if (result.matches && result.matches.length > 0) {
        const bestMatch = result.matches[0];
        console.log('✅ 找到匹配问题:', bestMatch.question_text);
        console.log('📊 相似度:', bestMatch.similarity_score);
        
        setMatchedQuestion(bestMatch);
      } else {
        console.log('❌ 未找到匹配问题');
        setMatchedQuestion(null);
      }
      
    } catch (error) {
      console.error('❌ 问题匹配失败:', error);
      setMatchError('问题匹配失败');
      setMatchedQuestion(null);
    } finally {
      setIsMatching(false);
    }
  }, [lastMatchTime]);

  // 清除匹配结果
  const clearMatchedQuestion = useCallback(() => {
    setMatchedQuestion(null);
    setMatchError('');
  }, []);
  
  // 智能分段处理函数
  const processTranscriptSegment = (text: string, confidence: number) => {
    const now = Date.now();
    const timeSinceLastSpeech = now - lastSpeechTime;
    
    // 更新最后语音时间
    setLastSpeechTime(now);
    
    // 如果是第一次识别或者距离上次识别超过2秒，开始新段落
    if (lastSpeechTime === 0 || timeSinceLastSpeech > 2000) {
      setSegmentStartTime(now);
      setCurrentSegment(text);
      
      // 如果有停顿，添加停顿标记
      if (lastSpeechTime !== 0 && timeSinceLastSpeech > 3000) {
        const pauseEntry = {
          id: `pause-${now}`,
          text: `[${Math.round(timeSinceLastSpeech / 1000)}s pause]`,
          timestamp: new Date().toLocaleTimeString(),
          confidence: 1.0,
          segmentType: 'pause' as const,
          duration: timeSinceLastSpeech / 1000
        };
        
        setTranscriptionHistory(prev => [...prev, pauseEntry]);
      }
    } else {
      // 继续当前段落
      setCurrentSegment(prev => prev + ' ' + text);
    }
    
    // 检查是否需要分段
    const combinedText = currentSegment + ' ' + text;
    const shouldCreateSegment = 
      text.endsWith('.') || 
      text.endsWith('!') || 
      text.endsWith('?') || 
      combinedText.length > 200 || // 超过200字符自动分段
      timeSinceLastSpeech > 5000; // 超过5秒停顿
    
    if (shouldCreateSegment) {
      const segmentType = 
        (text.endsWith('.') || text.endsWith('!') || text.endsWith('?')) ? 'sentence' :
        combinedText.length > 200 ? 'paragraph' : 'sentence';
      
      const newEntry = {
        id: `segment-${now}`,
        text: combinedText.trim(),
        timestamp: new Date().toLocaleTimeString(),
        confidence: confidence,
        segmentType: segmentType as 'sentence' | 'paragraph' | 'pause',
        duration: (now - segmentStartTime) / 1000
      };
      
      setTranscriptionHistory(prev => [...prev, newEntry]);
      setTranscript(prev => prev + ' ' + combinedText.trim());
      setCurrentSegment('');
      
      console.log('📝 分段完成:', combinedText.trim());
      
      // 检查是否需要生成AI回答
      if (shouldGenerateAnswer(combinedText.trim())) {
        console.log('🎯 检测到问题，准备生成AI回答');
        generateAIAnswer(combinedText.trim());
      }
      
      // 检查是否需要匹配历史问题
      if (questionMatchService.containsQuestion(combinedText.trim())) {
        console.log('🔍 检测到问题，开始匹配历史数据');
        handleQuestionMatch(combinedText.trim());
      }
    }
  };

  const formatTime = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  if (loading && !session) {
    return (
      <div className="min-h-screen bg-[#EEF9FF] flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-[#68C6F1] border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-[#3D3D3D]">Preparing formal interview...</p>
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
            onClick={() => navigate('/home')}
            className="px-6 py-2 bg-[#68C6F1] text-white rounded-lg hover:bg-[#5AB5E0] transition-colors"
          >
            Return to Home
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#EEF9FF]">
      {/* Header */}
      <div className="bg-white shadow-[0px_2px_8px_0px_rgba(145,215,255,0.2)] h-18 flex items-center justify-between px-6">
        <div className="flex items-center">
          {/* Logo */}
          <div className="flex items-center mr-8">
            <img src={logoImg} alt="OfferOtter Logo" className="w-8 h-8 mr-2" />
            <span className="text-[#A07161] font-bold text-sm">Offerotter</span>
          </div>
        </div>
        
        <div className="flex items-center gap-4">
          {/* Settings */}
          <button className="w-8 h-8 border border-dashed border-[#EEEEEE] rounded-md flex items-center justify-center">
            <svg className="w-5 h-5 text-[#393939]" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 8c1.1 0 2-.9 2-2s-.9-2-2-2-2 .9-2 2 .9 2 2 2zm0 2c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zm0 6c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2z"/>
            </svg>
          </button>
          
          {/* Microphone - Combined Recording & Speech Recognition */}
          <button 
            onClick={isRecording ? handleStopRecording : handleStartRecording}
            className={`w-8 h-8 border border-dashed border-[#EEEEEE] rounded-md flex items-center justify-center ${
              isRecording || isListening ? 'bg-red-50' : ''
            }`}
            title={isRecording || isListening ? '停止录制和语音识别' : '开始录制和语音识别'}
          >
            <svg className={`w-5 h-5 ${isRecording || isListening ? 'text-red-500' : 'text-[#393939]'}`} fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 14c1.66 0 2.99-1.34 2.99-3L15 5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3zm5.3-3c0 3-2.54 5.1-5.3 5.1S6.7 14 6.7 11H5c0 3.41 2.72 6.23 6 6.72V21h2v-3.28c3.28-.48 6-3.3 6-6.72h-1.7z"/>
            </svg>
          </button>
          
          {/* Leave Button */}
          <button 
            onClick={() => navigate('/home')}
            className="px-4 py-1 border border-dashed border-[#EEEEEE] rounded-full text-[#3D3D3D] text-sm flex items-center gap-2"
          >
            <svg className="w-5 h-5 text-red-500" fill="currentColor" viewBox="0 0 24 24">
              <circle cx="12" cy="12" r="10"/>
              <rect x="9" y="9" width="6" height="6" rx="1"/>
            </svg>
            Leave
          </button>
        </div>
      </div>

      {/* Main Content - Three Column Layout */}
      <div className="flex h-[calc(100vh-72px)] gap-6 p-6">
        {/* Left Column - Interviewer */}
        <div className="w-60 bg-white rounded-xl shadow-[0px_2px_8px_0px_rgba(145,215,255,0.2)] p-6">
          <div className="text-center mb-6">
            <div className="w-32 h-32 bg-gradient-to-br from-[#EEF9FF] to-[#D0F0FF] rounded-lg mx-auto mb-4 relative overflow-hidden">
              {/* Virtual Interviewer Avatar */}
              {!isScreenSharing && (
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="w-20 h-20 bg-[#68C6F1] rounded-full flex items-center justify-center">
                    <svg className="w-10 h-10 text-white" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
                    </svg>
                  </div>
                </div>
              )}
              
              {/* 屏幕共享视频显示 */}
              {isScreenSharing && (
                <video
                  ref={videoRef}
                  autoPlay
                  muted
                  className="absolute inset-0 w-full h-full object-cover rounded-lg"
                />
              )}
              
              {/* 屏幕共享状态指示器 - 覆盖在视频上方 */}
              {isScreenSharing && (
                <div className="absolute top-1 right-1 bg-green-500 text-white text-xs px-1 py-0.5 rounded flex items-center space-x-1">
                  <div className="w-1.5 h-1.5 bg-white rounded-full animate-pulse"></div>
                  <span>LIVE</span>
                </div>
              )}
            </div>
            <h3 
              className="font-semibold text-[#282828] mb-2 cursor-pointer hover:text-[#68C6F1] transition-colors"
              onClick={isScreenSharing ? handleStopScreenShare : handleStartScreenShare}
            >
              {isScreenSharing ? '🖥️ Stop Screen Share' : '🖥️ Interviewer says (Click to Share Screen)'}
            </h3>
          </div>
          
          {/* 语音识别控制区域 */}
          <div className="mb-6 p-4 bg-[#F8FCFF] border border-[#E0F2FF] rounded-lg">
            <div className="flex items-center justify-between mb-3">
              <div className="flex flex-col">
                <h4 className="text-sm font-medium text-[#282828]">Speech Recognition</h4>
                {shouldAutoRestart && (
                  <span className="text-xs text-green-600 flex items-center gap-1">
                    🔄 Auto-restart enabled
                  </span>
                )}
              </div>
              <button
                onClick={toggleSpeechRecognition}
                className={`px-3 py-1 rounded-full text-xs font-medium transition-all duration-200 ${
                  isListening
                    ? 'bg-red-500 hover:bg-red-600 text-white animate-pulse'
                    : 'bg-[#68C6F1] hover:bg-[#5AB5E0] text-white'
                }`}
              >
                {isListening ? '🛑 Stop' : '🎤 Start'}
              </button>
            </div>
            
            {/* 智能的转录状态显示区域 */}
            <div className="min-h-[60px] bg-white border border-gray-200 rounded p-2 text-xs flex items-center justify-center">
              {isListening ? (
                <div className="flex flex-col items-center space-y-1">
                  <div className="flex items-center space-x-2">
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-[#68C6F1] rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-[#68C6F1] rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                      <div className="w-2 h-2 bg-[#68C6F1] rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                    </div>
                    <span className="text-[#68C6F1] font-medium">Listening...</span>
                  </div>
                  
                  {/* 当前实时转录显示 */}
                  {interimTranscript && (
                    <div className="text-[#666666] italic text-center max-w-full">
                      "{interimTranscript.length > 30 ? interimTranscript.substring(0, 30) + '...' : interimTranscript}"
                    </div>
                  )}
                  
                  {/* no-speech 提示 */}
                  {noSpeechCount >= 2 && !interimTranscript && (
                    <div className="text-[#FFA500] text-center">
                      💡 Try speaking louder or check microphone
                    </div>
                  )}
                </div>
              ) : (
                <p className="text-[#999999] italic text-center">
                  Click "Start" to begin speech recognition
                </p>
              )}
            </div>
            
            {/* 转录历史控制 */}
            {transcriptionHistory.length > 0 && (
              <div className="mt-2 flex justify-between items-center">
                <span className="text-xs text-[#666666]">
                  {transcriptionHistory.length} entries
                </span>
                <button
                  onClick={clearTranscriptionHistory}
                  className="text-xs text-red-500 hover:text-red-700 transition-colors"
                >
                  Clear History
                </button>
              </div>
            )}
            
            {/* 错误提示和重试 */}
            {error && error.includes('麦克风') && (
              <div className="mt-2 p-2 bg-red-50 border border-red-200 rounded">
                <p className="text-xs text-red-700 mb-2">{error}</p>
                <button
                  onClick={() => {
                    setError('');
                    toggleSpeechRecognition();
                  }}
                  className="text-xs bg-red-100 hover:bg-red-200 text-red-700 px-2 py-1 rounded transition-colors"
                >
                  重试
                </button>
              </div>
            )}
          </div>
          
          {/* Speech Transcription History */}
          <div className="space-y-4">
            {/* Header */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-xs text-[#999999]">
                  <svg className="w-4 h-4 text-[#6FBDFF]" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 14c1.66 0 2.99-1.34 2.99-3L15 5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3zm5.3-3c0 3-2.54 5.1-5.3 5.1S6.7 14 6.7 11H5c0 3.41 2.72 6.23 6 6.72V21h2v-3.28c3.28-.48 6-3.3 6-6.72h-1.7z"/>
                  </svg>
                  Speech Transcription ({transcriptionHistory.length})
                </div>
                {transcriptionHistory.length > 0 && (
                  <button
                    onClick={clearTranscriptionHistory}
                    className="text-xs text-red-500 hover:text-red-700 transition-colors"
                  >
                    Clear All
                  </button>
                )}
              </div>
              
              {/* Timer */}
              <div className="text-xs text-[#999999] flex items-center gap-2">
                <svg className="w-4 h-4 text-[#6FBDFF]" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M15,1H9V3H15M11,14H13V8H11M19.03,7.39L20.45,5.97C20,5.46 19.55,5 19.04,4.56L17.62,6C16.07,4.74 14.12,4 12,4A9,9 0 0,0 3,13A9,9 0 0,0 12,22C17,22 21,17.97 21,13C21,10.88 20.26,8.93 19.03,7.39Z"/>
                </svg>
                {formatTime(3600 - timeRemaining)}
              </div>
            </div>
            
            {/* Transcription List */}
            <div className="flex-1 overflow-hidden">
              {transcriptionHistory.length === 0 ? (
                <div className="border border-dashed border-[#EEEEEE] rounded-lg p-6 text-center">
                  <div className="w-12 h-12 bg-[#F0F8FF] rounded-full flex items-center justify-center mx-auto mb-3">
                    <svg className="w-6 h-6 text-[#68C6F1]" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M12 14c1.66 0 2.99-1.34 2.99-3L15 5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3zm5.3-3c0 3-2.54 5.1-5.3 5.1S6.7 14 6.7 11H5c0 3.41 2.72 6.23 6 6.72V21h2v-3.28c3.28-.48 6-3.3 6-6.72h-1.7z"/>
                    </svg>
                  </div>
                  <p className="text-xs text-[#999999] leading-relaxed">
                    Start speech recognition to see your transcription here
                  </p>
                </div>
              ) : (
                <div className="max-h-[400px] overflow-y-auto space-y-3 bg-[#F8FCFF] border border-[#E0F2FF] rounded-lg p-3">
                  {transcriptionHistory.map((entry, index) => (
                    <div 
                      key={entry.id} 
                      className={`space-y-2 ${
                        entry.segmentType === 'pause' 
                          ? 'opacity-60 bg-gray-50' 
                          : entry.segmentType === 'paragraph'
                          ? 'border-l-4 border-[#68C6F1] pl-3 bg-blue-50'
                          : 'bg-white'
                      } p-2 rounded border border-gray-100`}
                    >
                      {/* Segment Header */}
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <span className="text-xs font-mono text-[#666666] bg-gray-100 px-1.5 py-0.5 rounded">
                            #{index + 1}
                          </span>
                          <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                            entry.segmentType === 'sentence' 
                              ? 'bg-green-100 text-green-700'
                              : entry.segmentType === 'paragraph'
                              ? 'bg-blue-100 text-blue-700'
                              : 'bg-gray-100 text-gray-600'
                          }`}>
                            {entry.segmentType === 'sentence' ? 'Sentence' :
                             entry.segmentType === 'paragraph' ? 'Paragraph' : 'Pause'}
                          </span>
                          <span className="text-xs text-[#999999]">{entry.timestamp}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          {entry.duration && (
                            <span className="text-xs text-[#999999] bg-gray-100 px-1.5 py-0.5 rounded">
                              {entry.duration.toFixed(1)}s
                            </span>
                          )}
                          <span className="text-xs text-[#68C6F1] bg-blue-100 px-1.5 py-0.5 rounded">
                            {Math.round(entry.confidence * 100)}%
                          </span>
                        </div>
                      </div>
                      
                      {/* Segment Content */}
                      <p className={`text-sm leading-relaxed ${
                        entry.segmentType === 'pause' 
                          ? 'text-[#999999] italic font-mono text-center'
                          : entry.segmentType === 'paragraph'
                          ? 'text-[#333333] font-medium'
                          : 'text-[#333333]'
                      }`}>
                        {entry.text}
                      </p>
                      
                      {/* Segment Separator */}
                      {index < transcriptionHistory.length - 1 && entry.segmentType !== 'pause' && (
                        <div className="border-t border-dashed border-[#E0F2FF] mt-2"></div>
                      )}
                    </div>
                  ))}
                  
                  {/* Current Segment Display */}
                  {currentSegment && (
                    <div className="bg-yellow-50 border-l-4 border-yellow-400 pl-3 p-2 rounded border border-yellow-200">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <span className="text-xs font-mono text-[#666666] bg-yellow-100 px-1.5 py-0.5 rounded">
                            #{transcriptionHistory.length + 1}
                          </span>
                          <span className="text-xs px-2 py-0.5 rounded-full font-medium bg-yellow-100 text-yellow-700">
                            Current
                          </span>
                        </div>
                        <div className="w-2 h-2 bg-yellow-500 rounded-full animate-pulse"></div>
                      </div>
                      <p className="text-sm text-[#333333] leading-relaxed font-medium">{currentSegment}</p>
                    </div>
                  )}
                  
                  {/* Real-time Transcription */}
                  {interimTranscript && (
                    <div className="bg-blue-50 border-l-4 border-blue-400 pl-3 p-2 rounded border border-blue-200">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <span className="text-xs px-2 py-0.5 rounded-full font-medium bg-blue-100 text-blue-700">
                            Real-time
                          </span>
                        </div>
                        <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
                      </div>
                      <p className="text-sm text-[#666666] italic leading-relaxed">{interimTranscript}</p>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Middle Column - Interview Copilot */}
        <div className="flex-1 bg-white rounded-xl shadow-[0px_2px_8px_0px_rgba(145,215,255,0.2)] p-6">
          {/* Section Header */}
          <div className="flex items-center gap-2 mb-6">
            <div className="w-6 h-1 bg-[#87D2F6] rounded-full"></div>
            <h2 className="font-semibold text-[#282828]">Interview Copilot</h2>
            <div className="ml-auto flex items-center gap-3">
              <div className="flex items-center gap-2">
                <div className={`w-8 h-4 rounded-full relative transition-colors ${
                  isGeneratingAnswer ? 'bg-orange-400' : 
                  isListening ? 'bg-green-500' : 'bg-gray-400'
                }`}>
                  <div className="w-3 h-3 bg-white rounded-full absolute right-0.5 top-0.5"></div>
                </div>
                              <span className="text-sm text-[#3D3D3D]">
                {isGeneratingAnswer ? 'Generating...' : 
                 isListening ? (shouldAutoRestart ? 'Listening & Auto-Restart Enabled' : 'Listening & AI Ready') : 'Click microphone to start'}
              </span>
              </div>
            </div>
          </div>
          
          {/* Dynamic Content Area */}
          <div className="space-y-4 mb-6 max-h-[600px] overflow-y-auto">
            {/* 空状态 */}
            {aiAnswers.length === 0 && !isGeneratingAnswer && (
              <div className="text-center py-12">
                <div className="w-16 h-16 bg-[#F0F8FF] rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-[#68C6F1]" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
                  </svg>
                </div>
                <p className="text-[#999999] text-sm mb-2">
                  Ask a question to get AI-powered suggestions
                </p>
                <p className="text-[#CCCCCC] text-xs mb-4">
                  Start speaking and I'll help you craft better answers
                </p>
              </div>
            )}
            
            {/* AI答案列表 */}
            {aiAnswers.map((aiItem, index) => (
              <div key={aiItem.id} className="space-y-3 border-b border-gray-100 pb-4 last:border-b-0">
                <div className="flex items-center justify-between">
                  <div className="text-sm text-[#999999]">
                    AI Suggestion #{index + 1} <span className="text-xs text-[#CCCCCC]">({aiItem.timestamp})</span>
                  </div>
                  <span className={`text-xs px-2 py-1 rounded-full ${
                    aiItem.isGenerating 
                      ? 'bg-orange-100 text-orange-700' 
                      : 'bg-green-100 text-green-700'
                  }`}>
                    {aiItem.isGenerating ? 'Generating...' : 'Generated'}
                  </span>
                </div>
                
                {/* 问题显示 */}
                <div className="text-xs text-[#666666] bg-blue-50 p-2 rounded border-l-2 border-blue-300">
                  <strong>Question:</strong> "{aiItem.question.substring(0, 100)}{aiItem.question.length > 100 ? '...' : ''}"
                </div>
                
                {/* 答案显示 */}
                {aiItem.isGenerating ? (
                  <div className="p-4 bg-orange-50 rounded-lg border-l-4 border-orange-400">
                    <div className="flex items-center gap-3">
                      <div className="w-4 h-4 border-2 border-orange-500 border-t-transparent rounded-full animate-spin"></div>
                      <span className="text-orange-700 text-sm font-medium">AI is analyzing your question...</span>
                    </div>
                  </div>
                ) : (
                  <div className="text-[#333333] leading-relaxed p-4 bg-gray-50 rounded-lg border-l-4 border-green-400 prose prose-sm max-w-none">
                    <ReactMarkdown 
                      remarkPlugins={[remarkGfm]}
                      components={{
                        // 自定义样式
                        h1: ({node, ...props}) => <h1 className="text-lg font-bold text-[#333333] mb-3 mt-0" {...props} />,
                        h2: ({node, ...props}) => <h2 className="text-base font-semibold text-[#333333] mb-2 mt-4" {...props} />,
                        h3: ({node, ...props}) => <h3 className="text-sm font-medium text-[#333333] mb-2 mt-3" {...props} />,
                        p: ({node, ...props}) => <p className="text-sm text-[#333333] mb-3 leading-relaxed" {...props} />,
                        ul: ({node, ...props}) => <ul className="list-disc list-inside mb-3 space-y-1" {...props} />,
                        ol: ({node, ...props}) => <ol className="list-decimal list-inside mb-3 space-y-1" {...props} />,
                        li: ({node, ...props}) => <li className="text-sm text-[#333333] leading-relaxed" {...props} />,
                        strong: ({node, ...props}) => <strong className="font-semibold text-[#333333]" {...props} />,
                        em: ({node, ...props}) => <em className="italic text-[#333333]" {...props} />,
                        code: ({node, ...props}) => <code className="bg-blue-100 text-blue-800 px-1 py-0.5 rounded text-xs font-mono" {...props} />,
                        pre: ({node, ...props}) => <pre className="bg-gray-100 p-3 rounded-lg overflow-x-auto mb-3" {...props} />,
                        blockquote: ({node, ...props}) => <blockquote className="border-l-4 border-blue-300 pl-3 italic text-[#666666] mb-3" {...props} />,
                        hr: ({node, ...props}) => <hr className="border-gray-300 my-4" {...props} />,
                        table: ({node, ...props}) => <table className="w-full border-collapse border border-gray-300 mb-3" {...props} />,
                        th: ({node, ...props}) => <th className="border border-gray-300 px-2 py-1 bg-gray-100 text-xs font-medium" {...props} />,
                        td: ({node, ...props}) => <td className="border border-gray-300 px-2 py-1 text-xs" {...props} />,
                      }}
                    >
                      {aiItem.answer}
                    </ReactMarkdown>
                  </div>
                )}
              </div>
            ))}
            
            {/* 底部操作区 */}
            {aiAnswers.length > 0 && (
              <div className="flex items-center justify-between pt-4 border-t border-gray-100">
                <div className="text-xs text-[#999999]">
                  Total answers: {aiAnswers.length}
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={regenerateAIAnswer}
                    disabled={isGeneratingAnswer || aiAnswers.length === 0}
                    className="flex items-center gap-2 text-[#3D3D3D] text-xs hover:text-[#68C6F1] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                    Regenerate Last
                  </button>
                  <button
                    onClick={clearAIAnswers}
                    className="flex items-center gap-2 text-red-500 text-xs hover:text-red-600 transition-colors"
                  >
                    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                    Clear All
                  </button>
                </div>
              </div>
            )}
            
            {/* 使用提示 */}
            {aiAnswers.length > 0 && (
              <div className="text-xs text-[#999999] bg-blue-50 p-3 rounded border-l-2 border-blue-300">
                💡 <strong>Tip:</strong> Use these suggestions as frameworks and personalize them with your own experiences
              </div>
            )}
          </div>
        </div>

        {/* Right Column - Question Bank */}
        <div className="w-96 bg-white rounded-xl shadow-[0px_2px_8px_0px_rgba(145,215,255,0.2)] p-6">
          {/* Section Header */}
          <div className="flex items-center gap-2 mb-6">
            <div className="w-6 h-1 bg-[#87D2F6] rounded-full"></div>
            <h2 className="font-semibold text-[#282828]">Question Bank</h2>
            {isMatching && (
              <div className="ml-auto">
                <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
              </div>
            )}
          </div>
          
          {/* 匹配的历史问题 */}
          {matchedQuestion ? (
            <div className="space-y-4">
              {/* 匹配状态指示 */}
              <div className="flex items-center gap-2 mb-4">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-xs text-green-600 font-medium">
                  Found similar question ({Math.round(matchedQuestion.similarity_score * 100)}% match)
                </span>
                <button
                  onClick={clearMatchedQuestion}
                  className="ml-auto text-gray-400 hover:text-gray-600 transition-colors"
                  title="Clear match"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              {/* 历史问题 */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="flex items-center gap-2 mb-2">
                  <div className="w-1 h-4 bg-blue-500 rounded-full"></div>
                  <span className="text-xs font-medium text-blue-700">Historical Question</span>
                </div>
                <h3 className="text-sm font-semibold text-[#333333] leading-snug mb-2">
                  {matchedQuestion.question_text}
                </h3>
                <div className="flex items-center gap-4 text-xs text-gray-500">
                  <span className="flex items-center gap-1">
                    <div className={`w-2 h-2 rounded-full ${
                      matchedQuestion.difficulty === 'easy' ? 'bg-green-400' :
                      matchedQuestion.difficulty === 'medium' ? 'bg-yellow-400' :
                      'bg-red-400'
                    }`}></div>
                    {matchedQuestion.difficulty}
                  </span>
                  <span className="text-gray-400">|</span>
                  <span>{matchedQuestion.question_type}</span>
                  <span className="text-gray-400">|</span>
                  <span>{matchedQuestion.session_title}</span>
                </div>
              </div>

              {/* 期望答案 */}
              {matchedQuestion.expected_answer && (
                <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <div className="w-1 h-4 bg-gray-500 rounded-full"></div>
                    <span className="text-xs font-medium text-gray-700">Expected Answer</span>
                  </div>
                  <div className="text-sm text-[#333333] leading-relaxed">
                    {matchedQuestion.expected_answer}
                  </div>
                </div>
              )}

              {/* 用户历史答案 */}
              {matchedQuestion.user_answer && (
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <div className="w-1 h-4 bg-green-500 rounded-full"></div>
                    <span className="text-xs font-medium text-green-700">Your Previous Answer</span>
                    {matchedQuestion.answered_at && (
                      <span className="text-xs text-gray-400 ml-auto">
                        {new Date(matchedQuestion.answered_at).toLocaleDateString()}
                      </span>
                    )}
                  </div>
                  <div className="text-sm text-[#333333] leading-relaxed">
                    {matchedQuestion.user_answer}
                  </div>
                </div>
              )}

              {/* 使用提示 */}
              <div className="text-xs text-[#999999] bg-yellow-50 p-3 rounded border-l-2 border-yellow-300">
                💡 <strong>Tip:</strong> Use your previous experience as a starting point and adapt it to the current context
              </div>
            </div>
          ) : (
            /* 空状态 */
            <div className="text-center py-12">
              <div className="w-16 h-16 bg-[#F0F8FF] rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-[#68C6F1]" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M9.5,3A6.5,6.5 0 0,1 16,9.5C16,11.11 15.41,12.59 14.44,13.73L14.71,14H15.5L20.5,19L19,20.5L14,15.5V14.71L13.73,14.44C12.59,15.41 11.11,16 9.5,16A6.5,6.5 0 0,1 3,9.5A6.5,6.5 0 0,1 9.5,3M9.5,5C7,5 5,7 5,9.5C5,12 7,14 9.5,14C12,14 14,12 14,9.5C14,7 12,5 9.5,5Z"/>
                </svg>
              </div>
              <p className="text-[#999999] text-sm mb-2">
                Ask a question to find similar ones from your history
              </p>
              <p className="text-[#CCCCCC] text-xs mb-4">
                Start speaking and I'll search your previous interviews
              </p>
              {matchError && (
                <p className="text-red-500 text-xs mt-2">
                  {matchError}
                </p>
              )}
            </div>
          )}
          
          {/* Answer Input - Hidden */}
          {/* 
          <div className="mt-6 space-y-4">
            <textarea
              value={answer}
              onChange={(e) => setAnswer(e.target.value)}
              placeholder="Type your answer here..."
              className="w-full h-32 p-3 border border-gray-200 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-[#68C6F1] focus:border-transparent text-sm"
            />
            
            <div className="flex gap-2">
              <button
                onClick={handleSubmitAnswer}
                disabled={!answer.trim() || loading}
                className="flex-1 py-2 bg-[#68C6F1] text-white rounded-lg hover:bg-[#5AB5E0] disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-sm font-medium"
              >
                {loading ? 'Submitting...' : 'Submit Answer'}
              </button>
              <button
                onClick={() => setAnswer('')}
                className="px-4 py-2 border border-gray-200 text-[#666] rounded-lg hover:border-gray-300 transition-colors text-sm"
              >
                Clear
              </button>
            </div>
          </div>
          */}
          
          {/* Progress - Hidden */}
          {/*
          <div className="mt-6 pt-4 border-t border-gray-100">
            <div className="flex items-center justify-between text-sm text-[#666] mb-2">
              <span>Progress</span>
              <span>{session?.current_question || 1}/{session?.total_questions || 15}</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-[#68C6F1] h-2 rounded-full transition-all duration-300"
                style={{ width: `${((session?.current_question || 1) / (session?.total_questions || 15)) * 100}%` }}
              ></div>
            </div>
            <div className="flex items-center justify-between text-xs text-[#999] mt-2">
              <span>Time: {formatTime(timeRemaining)}</span>
              <span>{currentQuestion?.difficulty || 'Medium'}</span>
            </div>
          </div>
          */}
        </div>
      </div>
    </div>
  );
};

export default FormalInterviewPage; 