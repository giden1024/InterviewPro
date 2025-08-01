import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useLocation } from 'react-router-dom';
import { questionService, Question, InterviewSession } from '../services/questionService';
import { resumeService, Resume } from '../services/resumeService';
import { interviewService } from '../services/interviewService';
import { Job } from '../services/jobService';
import { useAuthRedirect } from '../hooks/useAuthRedirect';
import logoImg from '../assets/logo02.png';

// 语音识别类型声明
declare global {
  interface Window {
    SpeechRecognition: typeof SpeechRecognition;
    webkitSpeechRecognition: typeof SpeechRecognition;
  }
}

interface SpeechRecognition extends EventTarget {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  start(): void;
  stop(): void;
  onstart: ((this: SpeechRecognition, ev: Event) => any) | null;
  onresult: ((this: SpeechRecognition, ev: SpeechRecognitionEvent) => any) | null;
  onerror: ((this: SpeechRecognition, ev: SpeechRecognitionErrorEvent) => any) | null;
  onend: ((this: SpeechRecognition, ev: Event) => any) | null;
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

declare var SpeechRecognition: {
  prototype: SpeechRecognition;
  new(): SpeechRecognition;
};

const MockInterviewPage: React.FC = () => {
  const location = useLocation();
  const { handleApiError } = useAuthRedirect();
  const [loading, setLoading] = useState(true);
  const [currentAnswer, setCurrentAnswer] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [conversationHistory, setConversationHistory] = useState<Array<{
    question: string;
    answer: string;
    timestamp: string;
  }>>([]);
  
  // 动态问题相关状态
  const [questions, setQuestions] = useState<Question[]>([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [interviewSession, setInterviewSession] = useState<InterviewSession | null>(null);
  const [userResume, setUserResume] = useState<Resume | null>(null);
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  // 语音识别相关状态
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [interimTranscript, setInterimTranscript] = useState('');
  const recognitionRef = useRef<SpeechRecognition | null>(null);

  // 新增状态：AI参考答案相关
  const [aiReferenceAnswers, setAIReferenceAnswers] = useState<Record<number, any>>({});
  const [isGeneratingReference, setIsGeneratingReference] = useState(false);
  const [referenceError, setReferenceError] = useState<string | null>(null);
  
  // 防止重复生成的ref
  const isGeneratingRef = useRef<Set<number>>(new Set());

  // 新增状态：语音合成相关
  const [isSpeaking, setIsSpeaking] = useState(false);

  // 获取当前问题
  const currentQuestion = questions[currentQuestionIndex];
  
  // 获取当前问题的AI参考答案
  const currentAIReferenceAnswer = currentQuestion ? aiReferenceAnswers[currentQuestion.id] : null;

  // 自动开始面试 - 获取用户简历并生成问题
  useEffect(() => {
    const initializeInterview = async () => {
      try {
        setLoading(true);
        setError(null);

        // 从路由状态获取选择的职位和简历ID
        const stateData = location.state as {
          sessionId?: string;
          selectedJob?: Job;
          resumeId?: number;
          questions?: Question[]; // 添加questions字段
        } | null;

        // 优先检查questions数据（从CompletePage传递过来）
        if (stateData?.questions && stateData?.sessionId) {
          console.log('✅ 使用已传递的问题数据:', stateData.sessionId);
          console.log(`📋 问题数量: ${stateData.questions.length}`);
          
          // 直接使用已传递的问题数据，避免重复API调用
          setQuestions(stateData.questions);
          
          // 只获取会话信息，不重新获取问题
          const sessionData = await questionService.getSessionQuestions(stateData.sessionId);
          setInterviewSession(sessionData.session);
          console.log('✅ 使用已传递的问题数据，避免重复生成');
        } else         if (stateData?.selectedJob && stateData?.resumeId) {
          // 使用从HomePage传递的数据
          setSelectedJob(stateData.selectedJob);
          console.log('Using selected position:', stateData.selectedJob.title);
          console.log('Using resume ID:', stateData.resumeId);

          // 获取简历详情
          const resumeData = await resumeService.getResume(stateData.resumeId);
          setUserResume(resumeData);
          console.log('Getting resume details:', resumeData.filename);

                    // 检查是否已经有会话ID和问题数据（从CompletePage传递过来）
          let questionData;
          let sessionData;
          if (stateData.sessionId && stateData.questions) {
            console.log('✅ 使用已存在的会话ID和问题数据:', stateData.sessionId);
            
            // 直接使用已传递的问题数据，避免重复API调用
            setQuestions(stateData.questions);
            
            // 获取会话信息（不包含问题，避免重复）
            sessionData = await questionService.getSessionQuestions(stateData.sessionId);
            setInterviewSession(sessionData.session);
            console.log(`✅ 使用已传递的问题数据，共 ${stateData.questions.length} 个`);
          } else if (stateData.sessionId) {
            console.log('✅ 使用已存在的会话ID，但需要获取问题:', stateData.sessionId);
            
            // 只有会话ID，需要获取问题
            questionData = await questionService.getSessionQuestions(stateData.sessionId);
            setQuestions(questionData.questions);
            setInterviewSession(questionData.session);
            console.log(`✅ 获取到的问题，共 ${questionData.questions.length} 个`);
          } else {
            // 只有在没有会话ID时才创建新的面试会话
            console.log('🆕 创建新的面试会话...');
            const interviewData = await interviewService.createInterview({
              resume_id: stateData.resumeId,
              interview_type: 'mock',
              total_questions: 8,
              difficulty_distribution: {
                'easy': 2,
                'medium': 4,
                'hard': 2
              },
              type_distribution: {
                'behavioral': 3,
                'technical': 2,
                'situational': 2,
                'experience': 1
              },
              custom_title: `${stateData.selectedJob.title} @ ${stateData.selectedJob.company} Mock Interview`
            });

            console.log('✅ 创建面试会话成功:', interviewData.session_id);

            // 然后基于会话ID生成问题
            questionData = await questionService.generateQuestions({
              resume_id: stateData.resumeId,
              session_id: interviewData.session_id
            });
            
            setQuestions(questionData.questions);
            setInterviewSession(questionData.session);
            console.log(`Successfully generated ${questionData.questions.length} questions`);
          }
          
          // 启动面试会话（仅当状态为 'created' 时）
          try {
            const sessionToUse = questionData?.session || sessionData?.session;
            if (!sessionToUse) {
              console.warn('⚠️ 无法获取会话信息，跳过启动步骤');
              return;
            }
            
            // 检查会话状态，只有在 'created' 状态时才启动面试
            if (sessionToUse.status === 'created') {
              console.log('🚀 会话状态为created，启动面试（默认逻辑）...');
              await interviewService.startInterview(sessionToUse.session_id);
              console.log('✅ Interview session started (default logic)');
            } else {
              console.log('ℹ️ 会话已启动，跳过启动步骤（默认逻辑），当前状态:', sessionToUse.status);
            }
          } catch (error) {
            console.error('❌ Failed to start interview session (default logic):', error);
            // 启动面试失败不应该阻止用户继续面试，只记录错误
            console.warn('⚠️ 面试启动失败（默认逻辑），但将继续进行面试流程');
          }
        } else {
          // 兼容旧的逻辑 - 自动获取最新简历
          console.log('No selected position and resume found, using default logic...');
          
          // 检查当前token是否有效
          const currentToken = localStorage.getItem('access_token');
          if (!currentToken) {
            throw new Error('No authentication token found. Please login again.');
          }
          
          console.log('🔐 Using current authentication token');

          const resumesResponse = await resumeService.getResumes({ 
            page: 1, 
            per_page: 50
          });
          
          // 修复：正确访问嵌套数据结构
          console.log('📄 Getting resume response:', resumesResponse);
          const allResumes = (resumesResponse as any)?.data?.resumes || resumesResponse?.resumes || [];
          console.log('📋 All resumes:', allResumes);
          
          const processedResumes = allResumes.filter((resume: any) => 
            resume.status === 'completed' || resume.status === 'processed'
          );
          console.log('✅ Processed resumes:', processedResumes);
          
          if (processedResumes.length === 0) {
            throw new Error('No completed resume found, please upload and analyze your resume first');
          }

          const latestResume = processedResumes[0];
          setUserResume(latestResume);

          // 首先创建面试会话
          const interviewData = await interviewService.createInterview({
            resume_id: latestResume.id,
            interview_type: 'mock',
            total_questions: 8,
            difficulty_distribution: {
              'easy': 2,
              'medium': 4,
              'hard': 2
            },
            type_distribution: {
              'behavioral': 3,
              'technical': 2,
              'situational': 2,
              'experience': 1
            },
            custom_title: `Mock Interview Based on ${latestResume.filename}`
          });

          // 然后基于会话ID生成问题
          const questionData = await questionService.generateQuestions({
            resume_id: latestResume.id,
            session_id: interviewData.session_id
          });

          setQuestions(questionData.questions);
          // ✅ 使用生成的会话但确保session_id正确
          const correctedSession = {
            ...questionData.session,
            session_id: interviewData.session_id  // 确保使用正确的session_id
          };
          setInterviewSession(correctedSession);
          console.log(`Successfully generated ${questionData.questions.length} questions`);
          console.log('✅ 使用的会话ID:', correctedSession.session_id);

          // 启动面试会话（仅当状态为 'created' 时）
          try {
            // 检查会话状态，只有在 'created' 状态时才启动面试
            if (correctedSession.status === 'created') {
              console.log('🚀 会话状态为created，启动面试（默认逻辑）...');
              await interviewService.startInterview(interviewData.session_id);
              console.log('✅ Interview session started (default logic)');
            } else {
              console.log('ℹ️ 会话已启动，跳过启动步骤（默认逻辑），当前状态:', correctedSession.status);
            }
          } catch (error) {
            console.error('❌ Failed to start interview session (default logic):', error);
            // 启动面试失败不应该阻止用户继续面试，只记录错误
            console.warn('⚠️ 面试启动失败（默认逻辑），但将继续进行面试流程');
          }
        }

        setLoading(false);
      } catch (error: any) {
        console.error('Failed to initialize interview:', error);
        
        // 检查是否是 token 相关错误
        if (error.message?.includes('token') || error.message?.includes('authentication')) {
          setError('Authentication failed. Please login again.');
          console.error('🔐 Token认证失败，请重新登录');
        } else {
          handleApiError(error);
          setError(error.message || 'Failed to initialize interview, please try again later');
        }
        setLoading(false);
      }
    };

    initializeInterview();
  }, [location.state]);

  // 初始化语音识别
  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      const recognition = new SpeechRecognition();
      
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = 'en-US';
      
      recognition.onstart = () => {
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
        
        if (finalTranscript) {
          setTranscript(prev => prev + finalTranscript);
          setCurrentAnswer(prev => prev + finalTranscript);
        }
        setInterimTranscript(interimTranscript);
      };
      
      recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);
      };
      
      recognition.onend = () => {
        setIsListening(false);
        setInterimTranscript('');
      };
      
      recognitionRef.current = recognition;
    }
    
    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, []);

  const handleSubmitAnswer = async () => {
    if (!currentAnswer.trim() || !currentQuestion || !interviewSession) return;

    try {
      console.log('📝 提交答案到数据库:', {
        sessionId: interviewSession.session_id,
        questionId: currentQuestion.id,
        answerText: currentAnswer.trim()
      });

      console.log('🔄 开始调用 interviewService.submitAnswer...');
      
      // 提交答案到数据库
      const submitResult = await interviewService.submitAnswer(interviewSession.session_id, {
        question_id: currentQuestion.id,
        answer_text: currentAnswer.trim(),
        response_time: 60 // 默认60秒，可以后续优化为实际计时
      });

      console.log('✅ 答案提交成功，结果:', submitResult);

      // 添加到对话历史
      setConversationHistory(prev => [...prev, {
        question: currentQuestion.question_text,
        answer: currentAnswer,
        timestamp: new Date().toLocaleTimeString()
      }]);

      // 清除当前答案和语音识别状态
      setCurrentAnswer('');
      setTranscript('');
      setInterimTranscript('');
      
      // 获取下一个问题
      if (currentQuestionIndex < questions.length - 1) {
        console.log('📝 提交答案，准备切换到下一个问题');
        console.log('🔢 当前问题索引:', currentQuestionIndex, '-> 下一个:', currentQuestionIndex + 1);
        
        // 注意：不再清除AI参考答案状态，因为我们要保留历史答案
        setIsGeneratingReference(false);
        setReferenceError(null);
        
        setCurrentQuestionIndex(prev => {
          const newIndex = prev + 1;
          console.log('🔄 问题索引更新:', prev, '->', newIndex);
          return newIndex;
        });
      } else {
        // 面试结束 - 结束面试会话
        console.log('🎉 面试已完成！结束面试会话...');
        try {
          await interviewService.endInterview(interviewSession.session_id);
          console.log('✅ 面试会话已结束');
        } catch (error) {
          console.error('❌ 结束面试会话失败:', error);
        }
      }
    } catch (error) {
      console.error('❌ 提交答案失败:', error);
      console.error('❌ 错误详情:', {
        message: error instanceof Error ? error.message : String(error),
        stack: error instanceof Error ? error.stack : undefined,
        name: error instanceof Error ? error.name : 'Unknown'
      });
      handleApiError(error);
      // 即使提交失败，也继续面试流程，只是不保存到数据库
      alert('答案提交失败，但面试将继续进行');
      
      // 添加到对话历史（本地保存）
      setConversationHistory(prev => [...prev, {
        question: currentQuestion.question_text,
        answer: currentAnswer,
        timestamp: new Date().toLocaleTimeString()
      }]);

      // 清除当前答案和语音识别状态
      setCurrentAnswer('');
      setTranscript('');
      setInterimTranscript('');
      
      // 继续到下一个问题
      if (currentQuestionIndex < questions.length - 1) {
        setCurrentQuestionIndex(prev => prev + 1);
      }
    }
  };

  const toggleRecording = () => {
    setIsRecording(!isRecording);
  };

  // 开始/停止语音识别
  const toggleSpeechRecognition = () => {
    if (!recognitionRef.current) {
      alert('Speech recognition is not supported in this browser.');
      return;
    }

    if (isListening) {
      recognitionRef.current.stop();
    } else {
      setTranscript('');
      setInterimTranscript('');
      recognitionRef.current.start();
    }
  };

  // 生成AI参考答案
  const generateAIReference = useCallback(async (question: Question) => {
    if (!question || isGeneratingReference) {
      console.log('Skipping AI reference generation:', { hasQuestion: !!question, isGenerating: isGeneratingReference });
      return;
    }
    
    // 如果已经有该问题的AI参考答案，直接返回
    if (aiReferenceAnswers[question.id]) {
      console.log('🔄 问题已有AI参考答案，无需重新生成:', question.id);
      return;
    }
    
    // 检查是否已经在生成该问题的答案
    if (isGeneratingRef.current.has(question.id)) {
      console.log('🔄 该问题的AI参考答案正在生成中，跳过:', question.id);
      return;
    }
    
    console.log('🤖 开始生成AI参考答案 for question:', question.id, question.question_text.substring(0, 50) + '...');
    console.log('🔄 当前AI参考答案状态:', aiReferenceAnswers);
    
    // Fallback参考答案
    const getFallbackReference = (question: Question) => {
      // 基于问题文本生成更具针对性的答案
      const questionText = question.question_text.toLowerCase();
      
      // 检测问题关键词来判断类型
      const isCareerGoal = questionText.includes('career') || questionText.includes('goal') || questionText.includes('future');
      const isStrength = questionText.includes('strength') || questionText.includes('strong') || questionText.includes('good at');
      const isWeakness = questionText.includes('weakness') || questionText.includes('improve') || questionText.includes('challenge');
      const isConflict = questionText.includes('disagree') || questionText.includes('conflict') || questionText.includes('difficult');
      const isTechnical = questionText.includes('technical') || questionText.includes('code') || questionText.includes('system');
      const isLeadership = questionText.includes('lead') || questionText.includes('manage') || questionText.includes('team');
      
      // 基于问题内容生成针对性答案
      if (isCareerGoal) {
        return {
          sample_answer: "I'm passionate about growing in this field and contributing to meaningful projects. My short-term goal is to excel in this role and master new technologies, while my long-term vision is to take on more strategic responsibilities and mentor others.",
          reference_answer: "Focus on aligning your career goals with the company's mission and growth opportunities. Show ambition while being realistic.",
          key_points: ["Show alignment with company goals", "Demonstrate growth mindset", "Be specific about timeline", "Show passion for the field"],
          structure_tips: "Current state → Short-term goals → Long-term vision → Why this role fits",
          difficulty: "medium",
          example_scenarios: ["Professional development", "Skill advancement", "Leadership aspirations", "Industry impact"],
          dos_and_donts: {
            dos: ["Be specific", "Show research about company", "Connect to role requirements", "Show ambition"],
            donts: ["Be too vague", "Focus only on salary", "Seem overconfident", "Ignore company culture"]
          },
          generated_by: "enhanced_fallback"
        };
      }
      
      if (isStrength) {
        return {
          sample_answer: "One of my key strengths is my ability to analyze complex problems and break them down into manageable solutions. In my previous role, this helped me improve our team's efficiency by 30% through process optimization.",
          reference_answer: "Choose strengths that are relevant to the job requirements and provide concrete examples with measurable results.",
          key_points: ["Choose job-relevant strengths", "Provide specific examples", "Quantify your impact", "Show how it benefits the employer"],
          structure_tips: "Strength → Example → Impact → How it applies to this role",
          difficulty: "easy",
          example_scenarios: ["Problem-solving abilities", "Communication skills", "Technical expertise", "Leadership qualities"],
          dos_and_donts: {
            dos: ["Be authentic", "Use specific examples", "Quantify results", "Connect to job needs"],
            donts: ["List generic strengths", "Be arrogant", "Choose irrelevant strengths", "Lack supporting examples"]
          },
          generated_by: "enhanced_fallback"
        };
      }
      
      if (isConflict) {
        return {
          sample_answer: "In my previous role, I disagreed with a teammate about the approach to a critical project. I scheduled a private meeting to understand their perspective, shared my concerns respectfully, and we found a compromise that incorporated both our ideas. The project was completed successfully and our working relationship improved.",
          reference_answer: "Use the STAR method to describe a real situation where you handled disagreement professionally and achieved a positive outcome.",
          key_points: ["Show respect for others", "Demonstrate problem-solving", "Focus on positive outcomes", "Highlight communication skills"],
          structure_tips: "Situation → Your approach → Actions taken → Positive result → Lessons learned",
          difficulty: "hard",
          example_scenarios: ["Project disagreements", "Process improvements", "Priority conflicts", "Team decisions"],
          dos_and_donts: {
            dos: ["Show maturity", "Focus on solutions", "Demonstrate respect", "Highlight learning"],
            donts: ["Blame others", "Avoid taking responsibility", "Show stubbornness", "Speak negatively"]
          },
          generated_by: "enhanced_fallback"
        };
      }
      
      if (isTechnical) {
        return {
          sample_answer: "I have strong experience with modern development practices including version control, testing, and deployment automation. In my recent project, I implemented a CI/CD pipeline that reduced deployment time by 50% and significantly improved code quality.",
          reference_answer: "Demonstrate your technical knowledge with specific examples and explain how your skills would benefit the team and projects.",
          key_points: ["Show relevant technical skills", "Provide concrete examples", "Explain your thought process", "Discuss best practices"],
          structure_tips: "Technology → Application → Results → Best practices → Future learning",
          difficulty: "medium",
          example_scenarios: ["System architecture", "Code optimization", "Tool implementation", "Technical challenges"],
          dos_and_donts: {
            dos: ["Be specific", "Show continuous learning", "Explain trade-offs", "Demonstrate impact"],
            donts: ["Be too theoretical", "Skip examples", "Oversimplify complex topics", "Ignore collaboration"]
          },
          generated_by: "enhanced_fallback"
        };
      }
      
      if (isLeadership) {
        return {
          sample_answer: "I led a cross-functional team of 5 people on a critical project with a tight deadline. I focused on clear communication, regular check-ins, and removing blockers for team members. We delivered the project on time and 15% under budget, and the team felt supported throughout the process.",
          reference_answer: "Highlight your leadership style, specific actions you took, and the positive outcomes for both the project and team members.",
          key_points: ["Describe your leadership style", "Show team development", "Highlight results", "Demonstrate emotional intelligence"],
          structure_tips: "Context → Leadership approach → Specific actions → Team outcomes → Personal growth",
          difficulty: "hard",
          example_scenarios: ["Team leadership", "Project management", "Mentoring others", "Change management"],
          dos_and_donts: {
            dos: ["Show servant leadership", "Highlight team success", "Demonstrate growth", "Be authentic"],
            donts: ["Take all credit", "Ignore team contributions", "Show micromanagement", "Be overly modest"]
          },
          generated_by: "enhanced_fallback"
        };
      }
      
      // 通用类型分类
      const typeReferences: Record<string, any> = {
        'behavioral': {
          sample_answer: "Let me share a specific example from my experience. When I faced a similar challenge, I took a structured approach: first analyzing the situation, then developing a plan, implementing it step by step, and finally measuring the results.",
          reference_answer: "Use the STAR method (Situation, Task, Action, Result) to structure your response with concrete examples from your experience.",
          key_points: ["Use STAR structure", "Provide specific examples", "Show your contribution", "Highlight results"],
          structure_tips: "Situation → Task → Action → Result",
          difficulty: "medium",
          example_scenarios: ["Team collaboration", "Problem solving", "Learning experience"],
          dos_and_donts: {
            dos: ["Be specific", "Take ownership", "Show growth"],
            donts: ["Blame others", "Be vague", "Focus only on team"]
          },
          generated_by: "enhanced_fallback"
        },
        'technical': {
          sample_answer: "From a technical perspective, I would approach this by first understanding the requirements, then evaluating different solutions based on factors like scalability, maintainability, and performance.",
          reference_answer: "Focus on demonstrating your technical knowledge, problem-solving approach, and best practices. Include specific examples if possible.",
          key_points: ["Explain concepts clearly", "Show practical experience", "Discuss best practices", "Mention trade-offs"],
          structure_tips: "Concept → Example → Best Practices → Considerations",
          difficulty: "hard",
          example_scenarios: ["Project implementation", "Technical challenges", "Tool selection"],
          dos_and_donts: {
            dos: ["Be specific", "Show experience", "Explain reasoning"],
            donts: ["Be too theoretical", "Skip examples", "Oversimplify"]
          },
          generated_by: "enhanced_fallback"
        },
        'situational': {
          sample_answer: "In this situation, I would start by gathering all relevant information, considering the different stakeholders involved, and evaluating the potential consequences of different approaches before making a decision.",
          reference_answer: "Think about how you would handle this scenario based on your experience and values. Show your decision-making process.",
          key_points: ["Analyze the situation", "Consider options", "Explain reasoning", "Show decision process"],
          structure_tips: "Analysis → Options → Decision → Rationale",
          difficulty: "medium",
          example_scenarios: ["Similar past situations", "Decision frameworks", "Risk assessment"],
          dos_and_donts: {
            dos: ["Think aloud", "Consider multiple angles", "Show judgment"],
            donts: ["Rush to answer", "Ignore context", "Be inflexible"]
          },
          generated_by: "enhanced_fallback"
        },
        'experience': {
          sample_answer: "Throughout my career, I've had several experiences that have shaped my professional growth. One particularly relevant example involved...",
          reference_answer: "Highlight relevant experiences from your background that demonstrate the skills and qualities mentioned in your resume.",
          key_points: ["Choose relevant examples", "Show your role", "Highlight achievements", "Connect to skills"],
          structure_tips: "Context → Your Role → Actions → Results → Learning",
          difficulty: "easy",
          example_scenarios: ["Key projects", "Achievements", "Growth experiences"],
          dos_and_donts: {
            dos: ["Be specific", "Quantify results", "Show progression"],
            donts: ["Be too general", "Downplay role", "Skip details"]
          },
          generated_by: "enhanced_fallback"
        }
      };
      
      return typeReferences[question.question_type] || {
        sample_answer: "This is an interesting question that allows me to share my perspective based on my experience and values. Let me think about the best way to approach this...",
        reference_answer: "Be authentic, show enthusiasm, and connect your answer to your experience and the role requirements.",
        key_points: ["Be authentic", "Show enthusiasm", "Stay relevant", "Use examples"],
        structure_tips: "Introduction → Main Points → Examples → Conclusion",
        difficulty: "medium",
        example_scenarios: ["Relevant experience"],
        dos_and_donts: {
          dos: ["Be genuine", "Stay positive", "Ask questions"],
          donts: ["Be vague", "Speak negatively", "Seem disinterested"]
        },
        generated_by: "enhanced_fallback"
      };
    };
    
    // 标记该问题正在生成
    isGeneratingRef.current.add(question.id);
    setIsGeneratingReference(true);
    setReferenceError(null);
    
    try {
      const response = await questionService.generateAIReferenceAnswer(question.id);
      console.log('✅ AI reference answer generated successfully:', response.ai_reference_answer);
      console.log('📝 Setting new AI reference answer to state...');
      
      // 将AI参考答案保存到对应的问题ID下
      setAIReferenceAnswers(prev => ({
        ...prev,
        [question.id]: response.ai_reference_answer
      }));
      
      // 强制触发重新渲染
      setTimeout(() => {
        console.log('🔍 Verifying AI reference answer state update:', response.ai_reference_answer);
      }, 100);
    } catch (error) {
      console.error('❌ Failed to generate AI reference answer:', error);
      setReferenceError('Failed to generate AI reference answer');
      // 使用fallback答案
      const fallbackAnswer = getFallbackReference(question);
      console.log('🔄 Using fallback answer:', fallbackAnswer);
      
      // 将fallback答案也保存到对应的问题ID下
      setAIReferenceAnswers(prev => ({
        ...prev,
        [question.id]: fallbackAnswer
      }));
    } finally {
      // 移除该问题ID标记
      isGeneratingRef.current.delete(question.id);
      setIsGeneratingReference(false);
    }
  }, [isGeneratingReference]); // ✅ 移除 aiReferenceAnswers 依赖以避免无限循环

  // 当问题变化时自动生成AI参考答案（优化版本）
  useEffect(() => {
    console.log('🔄 Question changed, checking if need to generate AI reference answer', { 
      currentQuestionIndex, 
      questionId: currentQuestion?.id, 
      questionText: currentQuestion?.question_text?.substring(0, 50) + '...',
      currentAIAnswer: currentAIReferenceAnswer ? 'exists' : 'null',
      isGenerating: isGeneratingReference
    });
    
          // 优化：只在用户开始回答问题时才生成AI参考答案
      if (currentQuestion && 
          !aiReferenceAnswers[currentQuestion.id] && 
          !isGeneratingReference &&
          currentAnswer.trim().length > 10) { // 只有当用户输入足够内容时才生成
        
        console.log('🧹 Clearing error state');
        setReferenceError(null);
        
        console.log('⏳ Preparing to generate new AI reference answer...');
        // 增加延迟，避免频繁调用
        setTimeout(() => {
          console.log('🚀 Starting to generate AI reference answer for new question');
          generateAIReference(currentQuestion);
        }, 1000); // 增加到1秒延迟
    } else {
      console.log('⏭️ Skipping AI generation:', {
        hasQuestion: !!currentQuestion,
        hasAnswer: !!aiReferenceAnswers[currentQuestion?.id],
        isGenerating: isGeneratingReference,
        hasUserInput: currentAnswer.trim().length > 10
      });
    }
  }, [currentQuestionIndex, currentQuestion?.id, currentAnswer]); // 添加currentAnswer依赖

  // 语音合成函数
  const speakText = useCallback((text: string) => {
    if ('speechSynthesis' in window) {
      // 停止当前正在播放的语音
      window.speechSynthesis.cancel();
      
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = 'en-US';
      utterance.rate = 0.9;
      utterance.pitch = 1;
      utterance.volume = 0.8;
      
      utterance.onstart = () => {
        setIsSpeaking(true);
      };
      
      utterance.onend = () => {
        setIsSpeaking(false);
      };
      
      utterance.onerror = () => {
        setIsSpeaking(false);
      };
      
      window.speechSynthesis.speak(utterance);
    } else {
      console.warn('Speech synthesis not supported in this browser');
    }
  }, []);

  // 监听当前问题变化，自动朗读
  useEffect(() => {
    if (currentQuestion && currentQuestion.question_text) {
      // 延迟一下再朗读，确保页面已经渲染完成
      const timer = setTimeout(() => {
        speakText(currentQuestion.question_text);
      }, 500);
      
      return () => clearTimeout(timer);
    }
  }, [currentQuestion, speakText]);

  // 页面卸载时停止语音合成
  useEffect(() => {
    return () => {
      if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
      }
    };
  }, []);

  // 错误状态显示
  if (error) {
    return (
      <div className="min-h-screen bg-[#EEF9FF] flex items-center justify-center">
        <div className="text-center p-8 bg-white rounded-xl shadow-lg max-w-md">
          <div className="text-red-500 text-4xl mb-4">⚠️</div>
          <h2 className="text-xl font-semibold text-gray-800 mb-4">Initialization Failed</h2>
          <p className="text-gray-600 mb-6">{error}</p>
          <button 
            onClick={() => window.location.reload()} 
            className="px-6 py-2 bg-[#6FBDFF] text-white rounded-lg hover:bg-[#5BADFF] transition-colors"
          >
            Reload
          </button>
        </div>
      </div>
    );
  }

  // 加载状态显示
  if (loading) {
    return (
      <div className="min-h-screen bg-[#EEF9FF] flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#6FBDFF] mx-auto mb-4"></div>
          <p className="text-gray-600">Generating interview questions based on your resume...</p>
          {userResume && (
            <p className="text-sm text-gray-500 mt-2">Resume: {userResume.filename}</p>
          )}
        </div>
      </div>
    );
  }

  // 没有问题时的显示
  if (!questions.length) {
    return (
      <div className="min-h-screen bg-[#EEF9FF] flex items-center justify-center">
        <div className="text-center p-8 bg-white rounded-xl shadow-lg max-w-md">
          <div className="text-yellow-500 text-4xl mb-4">📝</div>
          <h2 className="text-xl font-semibold text-gray-800 mb-4">No Interview Questions</h2>
          <p className="text-gray-600 mb-6">Failed to generate interview questions. Please check if your resume has been uploaded and analyzed.</p>
          <button 
            onClick={() => window.location.href = '/resume'} 
            className="px-6 py-2 bg-[#6FBDFF] text-white rounded-lg hover:bg-[#5BADFF] transition-colors"
          >
            Manage Resume
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#EEF9FF]">
      {/* 顶部导航栏 */}
      <div className="bg-white h-18 shadow-[0px_2px_8px_0px_rgba(145,215,255,0.2)] flex items-center justify-between px-6">
        <div className="flex items-center space-x-4">
          {/* Offerotter Logo */}
          <div className="flex items-center space-x-2">
            <img src={logoImg} alt="OfferOtter Logo" className="w-8 h-8" />
            <span className="text-[#A07161] font-semibold text-lg">Offerotter</span>
          </div>
        </div>
        
        <div className="flex items-center space-x-3">
          <button className="w-8 h-8 bg-white border border-dashed border-[#EEEEEE] rounded-md flex items-center justify-center">
            <svg className="w-5 h-5 text-[#393939]" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
            </svg>
          </button>
          <button className="w-8 h-8 bg-white border border-dashed border-[#EEEEEE] rounded-md flex items-center justify-center">
            <svg className="w-5 h-5 text-[#393939]" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 8c1.1 0 2-.9 2-2s-.9-2-2-2-2 .9-2 2 .9 2 2 2zm0 2c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zm0 6c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2z"/>
            </svg>
          </button>
          <button className="px-4 py-2 bg-white border border-dashed border-[#EEEEEE] rounded-full text-[#3D3D3D] text-sm flex items-center space-x-2">
            <svg className="w-4 h-4 text-[#F16868]" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
            </svg>
            <span>Leave</span>
          </button>
        </div>
      </div>

      {/* 主要内容区域 */}
      <div className="flex h-[calc(100vh-72px)] gap-6 p-6">
        {/* 左侧 - 面试官区域 */}
        <div className="w-60 bg-white rounded-xl shadow-[0px_2px_8px_0px_rgba(145,215,255,0.2)] p-6 flex flex-col">
          {/* 面试官头像 */}
          <div className="mb-6">
            <div className="relative">
              <div className="w-54 h-33 bg-gradient-to-br from-[#EEF9FF] to-[#D0F0FF] rounded-lg overflow-hidden mb-4">
                <div className="w-full h-full flex items-center justify-center">
                  {/* 面试官卡通头像 */}
                  <div className="w-20 h-20 relative">
                    <div className="w-full h-full bg-gradient-to-br from-[#F9E4D1] to-[#D0F0FF] rounded-full flex items-center justify-center">
                      <div className="w-16 h-16 bg-[#634B41] rounded-full flex items-center justify-center relative">
                        {/* 眼睛 */}
                        <div className="absolute top-4 left-3 w-2 h-2 bg-[#040300] rounded-full"></div>
                        <div className="absolute top-4 right-3 w-2 h-2 bg-[#040300] rounded-full"></div>
                        {/* 嘴巴 */}
                        <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 w-4 h-2 bg-[#664B40] rounded-full"></div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <span className="text-[#999999] text-xs">Interviewer says</span>
            </div>
          </div>

          {/* 当前问题 */}
          <div className="space-y-4 flex-1">
            <div className="flex items-center space-x-2 text-xs text-[#999999]">
              <svg className="w-6 h-6 text-[#6FBDFF]" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
              </svg>
              <span>01:23</span>
            </div>
            
            <div className="bg-white border border-dashed border-[#EEEEEE] rounded-lg p-4">
              <div className="flex items-start justify-between">
                <p className="text-[#282828] text-xs leading-relaxed flex-1 mr-3">
                  {currentQuestion.question_text}
                </p>
                <button
                  onClick={() => speakText(currentQuestion.question_text)}
                  disabled={isSpeaking}
                  className={`flex-shrink-0 p-1 rounded-full transition-colors ${
                    isSpeaking 
                      ? 'bg-blue-100 text-blue-600 animate-pulse' 
                      : 'bg-gray-100 hover:bg-blue-100 text-gray-600 hover:text-blue-600'
                  }`}
                  title={isSpeaking ? "Playing..." : "Replay Question"}
                >
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/>
                  </svg>
                </button>
              </div>
            </div>

            {/* 历史问题 */}
            {conversationHistory.length > 0 && (
              <div className="space-y-3">
                {conversationHistory.slice(-2).map((item, index) => (
                  <div key={index} className="space-y-2">
                    <div className="flex items-center space-x-2 text-xs text-[#999999]">
                      <svg className="w-6 h-6 text-[#6FBDFF]" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                      </svg>
                      <span>{item.timestamp}</span>
                    </div>
                    <div className="bg-white border border-dashed border-[#EEEEEE] rounded-lg p-4">
                      <p className="text-[#282828] text-xs leading-relaxed">
                        {item.question}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* 中间 - 面试助手区域 */}
        <div className="flex-1 bg-white rounded-xl shadow-[0px_2px_8px_0px_rgba(145,215,255,0.2)] p-6 flex flex-col">
          {/* 标题栏 */}
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-2">
              <div className="w-6 h-1.5 bg-[#87D2F6] rounded-full"></div>
              <h2 className="text-[#282828] text-base font-semibold">Interview Copilot</h2>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-4 bg-[#2F51FF] rounded-full relative">
                  <div className="absolute right-0 top-0 w-4 h-4 bg-white rounded-full shadow-sm"></div>
                </div>
                <span className="text-[#3D3D3D] text-sm">Auto Scroll</span>
              </div>
            </div>
          </div>

          {/* 分割线 */}
          <div className="w-full h-px bg-gradient-to-r from-transparent via-[rgba(0,110,200,0.22)] to-transparent mb-6"></div>

          {/* AI参考答案区域 */}
          <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-[#282828] text-sm font-medium">AI Reference Answer</h3>
              {currentQuestion && (
                <button
                  onClick={() => generateAIReference(currentQuestion)}
                  disabled={isGeneratingReference}
                  className="text-xs text-[#6FBDFF] hover:text-[#5BADFF] transition-colors disabled:opacity-50"
                >
                  {isGeneratingReference ? 'Generating...' : 'Regenerate'}
                </button>
              )}
            </div>
            
            {isGeneratingReference ? (
              <div className="flex items-center justify-center py-8">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-[#6FBDFF]"></div>
                <span className="ml-2 text-sm text-gray-500">Generating AI reference answer...</span>
              </div>
            ) : referenceError ? (
              <div className="text-red-500 text-sm py-4">
                {referenceError}
                {currentQuestion && (
                  <button
                    onClick={() => generateAIReference(currentQuestion)}
                    className="ml-2 text-[#6FBDFF] hover:text-[#5BADFF] underline"
                  >
                    Retry
                  </button>
                )}
              </div>
            ) : currentAIReferenceAnswer ? (
              <div className="space-y-4">
                {/* 示例答案 - 只显示这一部分 */}
                {currentAIReferenceAnswer.sample_answer && (
                  <div className="bg-[#F0F8FF] p-4 rounded-lg border-l-4 border-[#6FBDFF]">
                    <h4 className="text-sm font-medium text-[#282828] mb-2 flex items-center">
                      <svg className="w-4 h-4 text-[#6FBDFF] mr-2" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                      </svg>
                      Sample Answer
                    </h4>
                    <p className="text-sm text-gray-700 leading-relaxed">
                      {currentAIReferenceAnswer.sample_answer}
                    </p>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-gray-500 text-sm py-4">
                No reference answer available
              </div>
            )}
            
            {/* 原有的fallback显示（作为备用） */}
            {currentQuestion?.expected_answer && !currentAIReferenceAnswer && !isGeneratingReference && (
              <div className="bg-[#F8FEFF] p-4 rounded-lg border-l-4 border-[#6FBDFF]">
                <p className="text-sm text-gray-700 leading-relaxed">
                  {currentQuestion.expected_answer}
                </p>
                <button
                  onClick={() => currentQuestion && generateAIReference(currentQuestion)}
                  className="mt-3 px-4 py-2 bg-[#6FBDFF] hover:bg-[#5BADFF] text-white rounded-lg text-sm font-medium transition-colors"
                >
                  Generate AI Reference Answer
                </button>
              </div>
            )}
          </div>

          {/* 录音和输入区域 */}
          <div className="space-y-4">
            {/* 大录音按钮 - 隐藏 */}
            <div className="flex justify-center" style={{ display: 'none' }}>
              <button 
                onClick={toggleRecording}
                className={`w-16 h-16 rounded-full flex items-center justify-center transition-all duration-200 ${
                  isRecording 
                    ? 'bg-red-500 hover:bg-red-600 animate-pulse' 
                    : 'bg-[#6FBDFF] hover:bg-[#5BADFF]'
                }`}
              >
                <svg className="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 14c1.66 0 2.99-1.34 2.99-3L15 5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3zm5.3-3c0 3-2.54 5.1-5.3 5.1S6.7 14 6.7 11H5c0 3.41 2.72 6.23 6 6.72V21h2v-3.28c3.28-.48 6-3.3 6-6.72h-1.7z"/>
                </svg>
              </button>
            </div>
            
            {/* 文本输入框 */}
            <div className="space-y-3">
              <textarea
                value={currentAnswer}
                onChange={(e) => setCurrentAnswer(e.target.value)}
                placeholder="Type your answer here..."
                className="w-full h-24 p-4 border border-[#EEEEEE] rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-[#6FBDFF] focus:border-transparent"
              />
              
              <button
                onClick={handleSubmitAnswer}
                disabled={!currentAnswer.trim()}
                className="w-full py-3 bg-[#6FBDFF] hover:bg-[#5BADFF] disabled:bg-gray-300 text-white rounded-lg font-medium transition-colors"
              >
                Submit Answer
              </button>
            </div>

            {/* 语音识别区域 */}
            <div className="border-t border-[#EEEEEE] pt-4">
              <div className="flex items-center justify-between mb-3">
                <h4 className="text-[#282828] text-sm font-medium">Speech Recognition</h4>
                <button
                  onClick={toggleSpeechRecognition}
                  className={`px-4 py-2 rounded-lg font-medium text-sm transition-all duration-200 ${
                    isListening
                      ? 'bg-red-500 hover:bg-red-600 text-white animate-pulse'
                      : 'bg-[#6FBDFF] hover:bg-[#5BADFF] text-white'
                  }`}
                >
                  {isListening ? (
                    <div className="flex items-center space-x-2">
                      <div className="w-2 h-2 bg-white rounded-full animate-pulse"></div>
                      <span>Stop Listening</span>
                    </div>
                  ) : (
                    <div className="flex items-center space-x-2">
                      <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M12 14c1.66 0 2.99-1.34 2.99-3L15 5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3zm5.3-3c0 3-2.54 5.1-5.3 5.1S6.7 14 6.7 11H5c0 3.41 2.72 6.23 6 6.72V21h2v-3.28c3.28-.48 6-3.3 6-6.72h-1.7z"/>
                      </svg>
                      <span>Start Listening</span>
                    </div>
                  )}
                </button>
              </div>

              {/* 实时语音识别显示 */}
              <div className="bg-[#F8FCFF] border border-[#E0F2FF] rounded-lg p-4 min-h-[80px]">
                {isListening && (
                  <div className="flex items-center space-x-2 mb-2">
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-[#6FBDFF] rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-[#6FBDFF] rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                      <div className="w-2 h-2 bg-[#6FBDFF] rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                    </div>
                    <span className="text-[#6FBDFF] text-xs font-medium">Listening...</span>
                  </div>
                )}
                
                {transcript || interimTranscript ? (
                  <div className="space-y-2">
                    {transcript && (
                      <p className="text-[#333333] text-sm leading-relaxed">
                        {transcript}
                      </p>
                    )}
                    {interimTranscript && (
                      <p className="text-[#999999] text-sm leading-relaxed italic">
                        {interimTranscript}
                      </p>
                    )}
                  </div>
                ) : (
                  <p className="text-[#999999] text-sm">
                    {isListening 
                      ? 'Speak now, your speech will appear here in real-time...' 
                      : 'Click "Start Listening" to begin speech recognition'
                    }
                  </p>
                )}
              </div>

              {/* 语音识别提示 */}
              {!('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) && (
                <div className="mt-2 p-2 bg-yellow-50 border border-yellow-200 rounded text-yellow-800 text-xs">
                  Speech recognition is not supported in this browser. Please use Chrome or Edge for the best experience.
                </div>
              )}
            </div>
          </div>
        </div>

        {/* 右侧 - 题库区域 */}
        <div className="w-96 bg-white rounded-xl shadow-[0px_2px_8px_0px_rgba(145,215,255,0.2)] p-6 flex flex-col">
          {/* 标题栏 */}
          <div className="flex items-center space-x-2 mb-6">
            <div className="w-6 h-1.5 bg-[#87D2F6] rounded-full"></div>
            <h2 className="text-[#282828] text-base font-semibold">Question Bank</h2>
          </div>

          {/* 当前问题详情 */}
          <div className="mb-6">
            <div className="flex items-center gap-2 mb-3">
              <span className={`text-xs px-2 py-1 rounded-full ${
                currentQuestion.difficulty === 'easy' ? 'bg-green-100 text-green-600' :
                currentQuestion.difficulty === 'medium' ? 'bg-yellow-100 text-yellow-600' :
                'bg-red-100 text-red-600'
              }`}>
                {currentQuestion.difficulty}
              </span>
              <span className={`text-xs px-2 py-1 rounded ${
                currentQuestion.question_type === 'behavioral' ? 'text-[#6FBDFF] bg-blue-50' :
                currentQuestion.question_type === 'technical' ? 'text-purple-600 bg-purple-50' :
                currentQuestion.question_type === 'situational' ? 'text-orange-600 bg-orange-50' :
                currentQuestion.question_type === 'experience' ? 'text-green-600 bg-green-50' :
                'text-gray-600 bg-gray-50'
              }`}>
                {currentQuestion.question_type}
              </span>
              {currentQuestion.tags && currentQuestion.tags.length > 0 && (
                <span className="text-xs text-[#999999]">
                  {currentQuestion.tags.slice(0, 2).map(tag => `#${tag}`).join(' ')}
                </span>
              )}
            </div>
            
            <h3 className="text-[#333333] text-lg font-semibold leading-tight mb-4">
              {currentQuestion.question_text}
            </h3>
            
            {currentQuestion.expected_answer && (
              <div className="space-y-4">
                <h4 className="text-[#282828] text-sm font-medium">Expected Answer Framework</h4>
                <p className="text-[#333333] text-sm leading-relaxed">
                  {currentQuestion.expected_answer}
                </p>
              </div>
            )}
          </div>

          {/* 问题列表 */}
          <div className="flex-1 space-y-3">
            <h4 className="text-[#282828] text-sm font-medium">Upcoming Questions</h4>
            
            <div className="space-y-2">
              {questions.slice(currentQuestionIndex + 1, currentQuestionIndex + 4).map((question, index) => (
                <div key={index} className="p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs text-[#999999]">Question {currentQuestionIndex + index + 2}</span>
                    <span className={`text-xs px-2 py-1 rounded-full ${
                      question.difficulty === 'easy' ? 'bg-green-100 text-green-600' :
                      question.difficulty === 'medium' ? 'bg-yellow-100 text-yellow-600' :
                      'bg-red-100 text-red-600'
                    }`}>
                      {question.difficulty}
                    </span>
                  </div>
                  <p className="text-sm text-[#333333] line-clamp-2">
                    {question.question_text}
                  </p>
                  <div className="mt-2 flex items-center gap-2">
                    <span className={`text-xs px-2 py-1 rounded ${
                      question.question_type === 'behavioral' ? 'text-[#6FBDFF] bg-blue-50' :
                      question.question_type === 'technical' ? 'text-purple-600 bg-purple-50' :
                      question.question_type === 'situational' ? 'text-orange-600 bg-orange-50' :
                      question.question_type === 'experience' ? 'text-green-600 bg-green-50' :
                      'text-gray-600 bg-gray-50'
                    }`}>
                      {question.question_type}
                    </span>
                    {question.tags && question.tags.length > 0 && (
                      <span className="text-xs text-[#999999]">
                        {question.tags.slice(0, 1).map(tag => `#${tag}`).join(' ')}
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* 面试会话信息 */}
          {(selectedJob || userResume || interviewSession) && (
            <div className="mt-6 p-4 bg-[#F8FCFF] rounded-lg border border-[#E0F2FF]">
              <h4 className="text-[#282828] text-sm font-medium mb-3">Interview Session</h4>
              
              {selectedJob && (
                <div className="mb-3">
                  <div className="text-xs text-[#999999] mb-1">Target Position</div>
                  <div className="text-sm font-medium text-[#333333]">{selectedJob.title}</div>
                  <div className="text-xs text-[#666666]">{selectedJob.company}</div>
                  {selectedJob.location && (
                    <div className="text-xs text-[#999999] mt-1">{selectedJob.location}</div>
                  )}
                </div>
              )}
              
              {userResume && (
                <div className="mb-3">
                  <div className="text-xs text-[#999999] mb-1">Resume</div>
                  <div className="text-sm text-[#333333]">{userResume.filename}</div>
                  {userResume.skills && userResume.skills.length > 0 && (
                    <div className="flex flex-wrap gap-1 mt-2">
                      {userResume.skills.slice(0, 3).map((skill, index) => (
                        <span
                          key={index}
                          className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full"
                        >
                          {skill}
                        </span>
                      ))}
                      {userResume.skills.length > 3 && (
                        <span className="text-xs text-[#999999] px-2 py-1">
                          +{userResume.skills.length - 3} more
                        </span>
                      )}
                    </div>
                  )}
                </div>
              )}
              
              {interviewSession && (
                <div>
                  <div className="text-xs text-[#999999] mb-1">Session Info</div>
                  <div className="text-sm text-[#333333]">{interviewSession.title}</div>
                  <div className="text-xs text-[#666666] mt-1">
                    Type: {interviewSession.interview_type} • Status: {interviewSession.status}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* 统计信息 */}
          <div className="mt-6 p-4 bg-[#EEF9FF] rounded-lg">
            <div className="grid grid-cols-3 gap-4 text-center">
              <div>
                <div className="text-lg font-semibold text-[#6FBDFF]">
                  {currentQuestionIndex + 1}
                </div>
                <div className="text-xs text-[#999999]">Current</div>
              </div>
              <div>
                <div className="text-lg font-semibold text-[#6FBDFF]">
                  {questions.length}
                </div>
                <div className="text-xs text-[#999999]">Total</div>
              </div>
              <div>
                <div className="text-lg font-semibold text-[#6FBDFF]">
                  {conversationHistory.length}
                </div>
                <div className="text-xs text-[#999999]">Answered</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MockInterviewPage; 