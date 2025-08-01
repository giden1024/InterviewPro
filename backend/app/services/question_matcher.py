import logging
from typing import List, Dict, Any, Optional
from difflib import SequenceMatcher
import re
from sqlalchemy import and_

from app.extensions import db
from app.models.question import Question, Answer, InterviewSession, InterviewType
from app.utils.exceptions import ValidationError

logger = logging.getLogger(__name__)

"""Question matching service"""

class QuestionMatcher:
    def __init__(self):
        self.similarity_threshold = 0.6  # Similarity threshold
        self.min_query_length = 10  # Minimum query length
        
    def find_similar_questions(self, user_id: int, query_text: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Find similar questions in user's historical Formal Interview
        
        Args:
            user_id: User ID
            query_text: Query text (speech recognition result)
            limit: Return result count limit
            
        Returns:
            List of matched questions and answers
        """
        try:
            # Preprocess query text
            processed_query = self._preprocess_text(query_text)
            
            if len(processed_query) < self.min_query_length:
                logger.info(f"Query text too short, skip matching: {processed_query}")
                return []
            
            # Get all Formal Interview questions and answers for user
            qa_data = self._get_user_formal_interview_data(user_id)
            
            if not qa_data:
                logger.info(f"User {user_id} has no Formal Interview history data")
                return []
            
            # Calculate similarity and sort
            matches = []
            for item in qa_data:
                question_text = item['question_text']
                similarity = self._calculate_similarity(processed_query, question_text)
                
                if similarity >= self.similarity_threshold:
                    matches.append({
                        'question_id': item['question_id'],
                        'question_text': question_text,
                        'answer_text': item['answer_text'],
                        'similarity': similarity,
                        'session_id': item['session_id'],
                        'answered_at': item['answered_at'],
                        'score': item.get('score'),
                        'ai_feedback': item.get('ai_feedback')
                    })
            
            # Sort by similarity in descending order
            matches.sort(key=lambda x: x['similarity'], reverse=True)
            
            logger.info(f"Found {len(matches)} matching questions for user {user_id}")
            return matches[:limit]
            
        except Exception as e:
            logger.error(f"Question matching failed: {e}")
            return []
    
    def _get_user_formal_interview_data(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all Formal Interview question and answer data for user"""
        try:
            from app.models.question import Question, Answer, InterviewSession
            from app.models.question import InterviewType
            
            # Query all completed formal interview sessions and their questions/answers
            query = db.session.query(
                Question.id.label('question_id'),
                Question.question_text,
                Answer.answer_text,
                Answer.score,
                Answer.ai_feedback,
                Answer.answered_at,
                InterviewSession.session_id
            ).join(
                Answer, Question.id == Answer.question_id
            ).join(
                InterviewSession, Question.session_id == InterviewSession.id
            ).filter(
                InterviewSession.user_id == user_id,
                InterviewSession.interview_type == InterviewType.TECHNICAL,  # Only match formal interviews
                InterviewSession.status == 'completed'  # Only match completed interviews
            ).order_by(
                Answer.answered_at.desc()
            )
            
            results = query.all()
            
            return [{
                'question_id': row.question_id,
                'question_text': row.question_text,
                'answer_text': row.answer_text,
                'score': row.score,
                'ai_feedback': row.ai_feedback,
                'answered_at': row.answered_at.isoformat() if row.answered_at else None,
                'session_id': row.session_id
            } for row in results]
            
        except Exception as e:
            logger.error(f"Failed to get user formal interview data: {e}")
            return []
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text"""
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove punctuation (keep letters, numbers, spaces)
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts"""
        if not text1 or not text2:
            return 0.0
        
        # Preprocess both texts
        processed_text1 = self._preprocess_text(text1)
        processed_text2 = self._preprocess_text(text2)
        
        # Use SequenceMatcher to calculate similarity
        matcher = SequenceMatcher(None, processed_text1, processed_text2)
        sequence_similarity = matcher.ratio()
        
        # Additional keyword matching bonus
        words1 = set(processed_text1.split())
        words2 = set(processed_text2.split())
        
        if words1 and words2:
            keyword_overlap = len(words1.intersection(words2)) / len(words1.union(words2))
        else:
            keyword_overlap = 0.0
        
        # Comprehensive consideration of sequence similarity and keyword overlap
        final_similarity = 0.7 * sequence_similarity + 0.3 * keyword_overlap
        
        return min(1.0, final_similarity)
    
    def extract_question_from_speech(self, speech_text: str) -> str:
        """Extract question from speech recognition text"""
        if not speech_text:
            return ""
        
        # Simple question extraction logic
        # Can be enhanced as needed, such as using NLP techniques
        
        # Look for sentences ending with question marks
        question_patterns = [
            r'[^.!?]*\?[^.!?]*',  # Contains question mark
            r'[^.!?]*(?:what|how|why|when|where|which|who)[^.!?]*',  # Contains question words
        ]
        
        for pattern in question_patterns:
            matches = re.findall(pattern, speech_text, re.IGNORECASE)
            if matches:
                # Return the longest question (usually more complete)
                return max(matches, key=len).strip()
        
        # If no obvious question identifiers, check if it contains question words
        question_words = ['what', 'how', 'why', 'when', 'where', 'which', 'who', 'can', 'could', 'would', 'should']
        speech_lower = speech_text.lower()
        
        for word in question_words:
            if word in speech_lower:
                return speech_text.strip()
        
        return speech_text.strip() 