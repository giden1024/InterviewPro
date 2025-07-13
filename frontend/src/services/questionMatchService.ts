import { apiClient } from './api';

export interface HistoricalMatch {
  question_id: number;
  question_text: string;
  expected_answer: string;
  user_answer: string;
  session_title: string;
  answered_at: string | null;
  similarity_score: number;
  question_type: string;
  difficulty: string;
}

export interface QuestionMatchResult {
  matches: HistoricalMatch[];
  extracted_question: string | null;
  total_matches: number;
  speech_text: string;
  message?: string;
}

export interface QuestionMatchRequest {
  speech_text: string;
  limit?: number;
}

class QuestionMatchService {
  /**
   * 匹配历史问题
   */
  async matchHistoricalQuestion(data: QuestionMatchRequest): Promise<QuestionMatchResult> {
    try {
      const response: any = await apiClient.post('/interviews/match-question', {
        speech_text: data.speech_text,
        limit: data.limit || 3
      });
      
      return response.data;
    } catch (error) {
      console.error('问题匹配失败:', error);
      throw error;
    }
  }

  /**
   * 检查文本是否包含问题
   */
  containsQuestion(text: string): boolean {
    if (!text || text.length < 10) return false;
    
    const questionPatterns = [
      /\b(what|how|why|when|where|who|which)\b/i,
      /\b(can|could|would|should|do|does|did)\b/i,
      /\b(is|are|was|were)\b.*\?/i,
      /\b(tell me|describe|explain|give me)\b/i,
      /\b(experience|background|strength|weakness|challenge)\b/i,
      /\?/
    ];
    
    return questionPatterns.some(pattern => pattern.test(text));
  }

  /**
   * 从文本中提取最可能的问题
   */
  extractPotentialQuestion(text: string): string | null {
    if (!text) return null;
    
    // 按句子分割
    const sentences = text.split(/[.!?]+/).map(s => s.trim()).filter(s => s.length > 0);
    
    // 寻找包含问题标识的句子
    for (const sentence of sentences) {
      if (this.containsQuestion(sentence)) {
        return sentence;
      }
    }
    
    // 如果整个文本看起来像问题，返回整个文本
    if (this.containsQuestion(text)) {
      return text.trim();
    }
    
    return null;
  }

  /**
   * 防抖处理语音识别结果
   */
  private debounceTimer: NodeJS.Timeout | null = null;
  
  debounceMatch(
    speechText: string, 
    callback: (result: QuestionMatchResult | null) => void,
    delay: number = 2000
  ): void {
    if (this.debounceTimer) {
      clearTimeout(this.debounceTimer);
    }
    
    this.debounceTimer = setTimeout(async () => {
      try {
        if (this.containsQuestion(speechText)) {
          const result = await this.matchHistoricalQuestion({ speech_text: speechText });
          callback(result);
        } else {
          callback(null);
        }
      } catch (error) {
        console.error('防抖匹配失败:', error);
        callback(null);
      }
    }, delay);
  }

  /**
   * 清除防抖定时器
   */
  clearDebounce(): void {
    if (this.debounceTimer) {
      clearTimeout(this.debounceTimer);
      this.debounceTimer = null;
    }
  }
}

// 导出单例实例
export const questionMatchService = new QuestionMatchService(); 