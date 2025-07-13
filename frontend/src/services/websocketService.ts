// WebSocket service class
export class WebSocketService {
  private socket: WebSocket | null = null;
  private url: string;
  private reconnectInterval: number = 5000;
  private maxReconnectAttempts: number = 5;
  private reconnectAttempts: number = 0;
  private listeners: Map<string, Function[]> = new Map();

  constructor(url: string = 'ws://localhost:5001') {
    this.url = url;
  }

      /**
     * Connect to WebSocket
     */
  connect(token?: string): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        const wsUrl = token ? `${this.url}?token=${token}` : this.url;
        this.socket = new WebSocket(wsUrl);

        this.socket.onopen = () => {
          console.log('WebSocket connection established');
          this.reconnectAttempts = 0;
          resolve();
        };

        this.socket.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            this.handleMessage(data);
          } catch (error) {
            console.error('Failed to parse WebSocket message:', error);
          }
        };

        this.socket.onclose = (event) => {
          console.log('WebSocket连接已关闭:', event.code, event.reason);
          this.handleReconnect();
        };

        this.socket.onerror = (error) => {
          console.error('WebSocket错误:', error);
          reject(error);
        };
      } catch (error) {
        reject(error);
      }
    });
  }

  /**
   * 断开连接
   */
  disconnect(): void {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
  }

  /**
   * 发送消息
   */
  send(type: string, data: any): void {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      const message = JSON.stringify({ type, data });
      this.socket.send(message);
    } else {
      console.warn('WebSocket未连接，无法发送消息');
    }
  }

  /**
   * 监听消息
   */
  on(eventType: string, callback: Function): void {
    if (!this.listeners.has(eventType)) {
      this.listeners.set(eventType, []);
    }
    this.listeners.get(eventType)!.push(callback);
  }

  /**
   * 移除监听器
   */
  off(eventType: string, callback?: Function): void {
    if (callback) {
      const listeners = this.listeners.get(eventType) || [];
      const index = listeners.indexOf(callback);
      if (index !== -1) {
        listeners.splice(index, 1);
      }
    } else {
      this.listeners.delete(eventType);
    }
  }

  /**
   * 处理消息
   */
  private handleMessage(message: any): void {
    const { type, data } = message;
    const listeners = this.listeners.get(type) || [];
    listeners.forEach(listener => {
      try {
        listener(data);
      } catch (error) {
        console.error('WebSocket消息处理错误:', error);
      }
    });
  }

  /**
   * 处理重连
   */
  private handleReconnect(): void {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`尝试重连WebSocket (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
      
      setTimeout(() => {
        const token = localStorage.getItem('access_token');
        this.connect(token || undefined).catch(error => {
          console.error('WebSocket重连失败:', error);
        });
      }, this.reconnectInterval);
    } else {
      console.error('WebSocket重连失败，已达到最大重试次数');
    }
  }

  /**
   * 获取连接状态
   */
  get isConnected(): boolean {
    return this.socket?.readyState === WebSocket.OPEN;
  }
}

// 面试相关的WebSocket事件类型
export interface InterviewWebSocketEvents {
  // 面试开始
  'interview_started': {
    session_id: string;
    question: any;
  };

  // 新问题
  'new_question': {
    session_id: string;
    question: any;
    question_number: number;
  };

  // 答案提交确认
  'answer_submitted': {
    session_id: string;
    question_id: number;
    status: 'success' | 'error';
    message?: string;
  };

  // 面试结束
  'interview_completed': {
    session_id: string;
    summary: any;
  };

  // 语音转录结果
  'transcription_result': {
    session_id: string;
    question_id: number;
    transcript: string;
    confidence: number;
  };

  // 实时分析
  'analysis_update': {
    session_id: string;
    analysis: any;
  };

  // 错误通知
  'error': {
    code: string;
    message: string;
  };
}

// 面试WebSocket服务
export class InterviewWebSocketService extends WebSocketService {
  /**
   * 加入面试房间  
   */
  joinInterview(sessionId: string): void {
    this.send('join_interview', { session_id: sessionId });
  }

  /**
   * 离开面试房间
   */
  leaveInterview(sessionId: string): void {
    this.send('leave_interview', { session_id: sessionId });
  }

  /**
   * 提交答案
   */
  submitAnswer(sessionId: string, questionId: number, answer: string): void {
    this.send('submit_answer', {
      session_id: sessionId,
      question_id: questionId,
      answer
    });
  }

  /**
   * 请求下一个问题
   */
  requestNextQuestion(sessionId: string): void {
    this.send('next_question', { session_id: sessionId });
  }

  /**
   * 开始语音转录
   */
  startTranscription(sessionId: string, questionId: number): void {
    this.send('start_transcription', {
      session_id: sessionId,
      question_id: questionId
    });
  }

  /**
   * 结束语音转录
   */
  stopTranscription(sessionId: string): void {
    this.send('stop_transcription', { session_id: sessionId });
  }

  /**
   * 监听面试事件
   */
  onInterviewEvent<K extends keyof InterviewWebSocketEvents>(
    event: K, 
    callback: (data: InterviewWebSocketEvents[K]) => void
  ): void {
    this.on(event, callback);
  }
}

// 导出单例实例
export const websocketService = new WebSocketService();
export const interviewWebSocketService = new InterviewWebSocketService(); 