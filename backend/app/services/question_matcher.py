import logging
from typing import List, Dict, Any, Optional
from difflib import SequenceMatcher
import re
from sqlalchemy import and_

from app.extensions import db
from app.models.question import Question, Answer, InterviewSession, InterviewType
from app.utils.exceptions import ValidationError

logger = logging.getLogger(__name__)

class QuestionMatcher:
    """问题匹配服务"""
    
    def __init__(self):
        self.similarity_threshold = 0.6  # 相似度阈值
        self.min_query_length = 10  # 最小查询长度
    
    def find_similar_questions(
        self, 
        user_id: int, 
        query_text: str, 
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        在用户的历史Formal Interview中查找相似问题
        
        Args:
            user_id: 用户ID
            query_text: 查询文本（语音识别结果）
            limit: 返回结果数量限制
            
        Returns:
            匹配的问题和答案列表
        """
        try:
            # 预处理查询文本
            processed_query = self._preprocess_text(query_text)
            
            if len(processed_query) < self.min_query_length:
                logger.info(f"查询文本太短，跳过匹配: {processed_query}")
                return []
            
            # 获取用户所有Formal Interview的问题和答案
            historical_data = self._get_user_formal_interview_data(user_id)
            
            if not historical_data:
                logger.info(f"用户 {user_id} 没有Formal Interview历史数据")
                return []
            
            # 计算相似度并排序
            matches = []
            for item in historical_data:
                similarity = self._calculate_similarity(processed_query, item['question_text'])
                
                if similarity >= self.similarity_threshold:
                    matches.append({
                        'question_id': item['question_id'],
                        'question_text': item['question_text'],
                        'expected_answer': item['expected_answer'],
                        'user_answer': item['user_answer'],
                        'session_title': item['session_title'],
                        'answered_at': item['answered_at'],
                        'similarity_score': similarity,
                        'question_type': item['question_type'],
                        'difficulty': item['difficulty']
                    })
            
            # 按相似度降序排序
            matches.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            logger.info(f"为用户 {user_id} 找到 {len(matches)} 个匹配问题")
            return matches[:limit]
            
        except Exception as e:
            logger.error(f"问题匹配失败: {e}")
            return []
    
    def _get_user_formal_interview_data(self, user_id: int) -> List[Dict[str, Any]]:
        """获取用户所有Formal Interview的问题和答案数据"""
        query = db.session.query(
            Question.id.label('question_id'),
            Question.question_text,
            Question.expected_answer,
            Question.question_type,
            Question.difficulty,
            Answer.answer_text.label('user_answer'),
            Answer.answered_at,
            InterviewSession.title.label('session_title'),
            InterviewSession.session_id
        ).join(
            InterviewSession, Question.session_id == InterviewSession.id
        ).outerjoin(
            Answer, and_(
                Answer.question_id == Question.id,
                Answer.user_id == user_id
            )
        ).filter(
            and_(
                Question.user_id == user_id,
                InterviewSession.interview_type == InterviewType.TECHNICAL,  # 只匹配正式面试
                InterviewSession.status == 'completed'  # 只匹配已完成的面试
            )
        ).order_by(Answer.answered_at.desc())
        
        results = []
        for row in query.all():
            results.append({
                'question_id': row.question_id,
                'question_text': row.question_text,
                'expected_answer': row.expected_answer or '',
                'user_answer': row.user_answer or '',
                'session_title': row.session_title,
                'answered_at': row.answered_at.isoformat() if row.answered_at else None,
                'question_type': row.question_type.value if row.question_type else '',
                'difficulty': row.difficulty.value if row.difficulty else ''
            })
        
        return results
    
    def _preprocess_text(self, text: str) -> str:
        """预处理文本"""
        if not text:
            return ""
        
        # 转换为小写
        text = text.lower()
        
        # 移除多余的空白字符
        text = re.sub(r'\s+', ' ', text).strip()
        
        # 移除标点符号（保留字母、数字、空格）
        text = re.sub(r'[^\w\s]', '', text)
        
        return text
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """计算两个文本的相似度"""
        if not text1 or not text2:
            return 0.0
        
        # 预处理两个文本
        processed_text1 = self._preprocess_text(text1)
        processed_text2 = self._preprocess_text(text2)
        
        # 使用SequenceMatcher计算相似度
        similarity = SequenceMatcher(None, processed_text1, processed_text2).ratio()
        
        # 额外的关键词匹配加分
        keywords1 = set(processed_text1.split())
        keywords2 = set(processed_text2.split())
        
        if keywords1 and keywords2:
            keyword_overlap = len(keywords1.intersection(keywords2)) / len(keywords1.union(keywords2))
            # 综合考虑序列相似度和关键词重叠度
            similarity = (similarity * 0.7) + (keyword_overlap * 0.3)
        
        return round(similarity, 3)
    
    def extract_question_from_speech(self, speech_text: str) -> Optional[str]:
        """从语音识别文本中提取问题"""
        if not speech_text:
            return None
        
        # 简单的问题提取逻辑
        # 可以根据需要增强，比如使用NLP技术
        
        # 寻找问号结尾的句子
        sentences = re.split(r'[.!?]', speech_text)
        questions = [s.strip() for s in sentences if '?' in s or self._looks_like_question(s)]
        
        if questions:
            # 返回最长的问题（通常更完整）
            return max(questions, key=len).strip()
        
        # 如果没有明显的问题标识，检查是否包含疑问词
        if self._contains_question_words(speech_text):
            return speech_text.strip()
        
        return None
    
    def _looks_like_question(self, text: str) -> bool:
        """判断文本是否看起来像问题"""
        question_patterns = [
            r'\b(what|how|why|when|where|who|which|can|could|would|should|do|does|did|is|are|was|were)\b',
            r'\b(tell me|describe|explain|give me)\b',
            r'\b(experience|background|strength|weakness|challenge)\b'
        ]
        
        text_lower = text.lower()
        return any(re.search(pattern, text_lower) for pattern in question_patterns)
    
    def _contains_question_words(self, text: str) -> bool:
        """检查文本是否包含疑问词"""
        question_words = [
            'what', 'how', 'why', 'when', 'where', 'who', 'which',
            'can', 'could', 'would', 'should', 'do', 'does', 'did',
            'is', 'are', 'was', 'were', 'tell me', 'describe', 'explain'
        ]
        
        text_lower = text.lower()
        return any(word in text_lower for word in question_words) 