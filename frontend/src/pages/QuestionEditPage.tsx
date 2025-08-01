import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { questionService } from '../services/questionService';
import { interviewService } from '../services/interviewService';

interface Question {
  id: number;
  question_text: string;
  question_type: string;
  difficulty: string;
  category: string;
  tags: string[];
  expected_answer?: string;
  evaluation_criteria?: any;
  ai_context?: any;
  created_at: string;
  session_id?: number; // 修改为可选的，与questionService返回的类型保持一致
  latest_answer?: {
    id: number;
    answer_text: string;
    score?: number;
    answered_at: string;
  };
}

const QuestionEditPage: React.FC = () => {
  const { questionId } = useParams<{ questionId: string }>();
  const navigate = useNavigate();
  
  const [question, setQuestion] = useState<Question | null>(null);
  const [answer, setAnswer] = useState<string>('');
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 加载问题详情
  const loadQuestion = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      const response = await questionService.getQuestionDetail(Number(questionId));
      setQuestion(response.question);
      
      // 如果有现有答案，加载它
      if ((response.question as any).latest_answer) {
        setAnswer((response.question as any).latest_answer.answer_text);
      }
    } catch (error) {
      console.error('加载问题失败:', error);
      // 如果问题不存在或不属于当前用户，自动重定向到首页
      if (error instanceof Error && error.message.includes('Question not found')) {
        alert('问题不存在或您没有权限访问此问题，正在返回首页...');
        navigate('/home');
        return;
      }
      setError('加载问题失败，请重试');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSave = async () => {
    if (!answer.trim()) {
      setError('请输入答案内容');
      return;
    }

    if (!question?.session_id) {
      setError('会话信息缺失，无法保存答案');
      return;
    }

    try {
      setIsSaving(true);
      setError(null);

      // 使用interviewService提交答案
      await interviewService.submitAnswer(question.session_id.toString(), {
        question_id: question.id,
        answer_text: answer,
        response_time: 0 // 编辑模式下不计算响应时间
      });

      alert('答案保存成功！');
      navigate('/home');
    } catch (error) {
      console.error('保存答案失败:', error);
      setError('保存答案失败，请重试');
    } finally {
      setIsSaving(false);
    }
  };

  const handleCancel = () => {
    navigate('/home');
  };

  useEffect(() => {
    if (questionId) {
      loadQuestion();
    }
  }, [questionId]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">加载问题中...</p>
        </div>
      </div>
    );
  }

  if (error && !question) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-500 text-xl mb-4">⚠️</div>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={() => navigate('/home')}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            返回首页
          </button>
        </div>
      </div>
    );
  }

  if (!question) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600 mb-4">问题不存在</p>
          <button
            onClick={() => navigate('/home')}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            返回首页
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        {/* 头部 */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-2xl font-bold text-gray-900">编辑问题答案</h1>
            <div className="flex gap-3">
              <button
                onClick={handleCancel}
                className="px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50"
                disabled={isSaving}
              >
                取消
              </button>
              <button
                onClick={handleSave}
                disabled={isSaving || !answer.trim()}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                {isSaving && (
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                )}
                {isSaving ? '保存中...' : '保存答案'}
              </button>
            </div>
          </div>
          
          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-600 text-sm">{error}</p>
            </div>
          )}
        </div>

        {/* 问题信息 */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <div className="mb-4">
            <div className="flex items-center gap-2 mb-2">
              <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                {question.question_type}
              </span>
              <span className={`px-2 py-1 text-xs rounded-full ${
                question.difficulty === 'easy' ? 'bg-green-100 text-green-800' :
                question.difficulty === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                'bg-red-100 text-red-800'
              }`}>
                {question.difficulty}
              </span>
              <span className="px-2 py-1 bg-gray-100 text-gray-800 text-xs rounded-full">
                {question.category}
              </span>
            </div>
            <h2 className="text-lg font-semibold text-gray-900 mb-2">
              问题内容
            </h2>
            <p className="text-gray-700 leading-relaxed">
              {question.question_text}
            </p>
          </div>

          {question.tags && question.tags.length > 0 && (
            <div className="mb-4">
              <h3 className="text-sm font-medium text-gray-900 mb-2">标签</h3>
              <div className="flex flex-wrap gap-2">
                {question.tags.map((tag, index) => (
                  <span
                    key={index}
                    className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* 答案编辑区 */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            我的答案
          </h2>
          <textarea
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
            placeholder="请输入你的答案..."
            className="w-full h-64 p-4 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            disabled={isSaving}
          />
          <div className="mt-2 text-right">
            <span className="text-sm text-gray-500">
              {answer.length} 字符
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default QuestionEditPage; 