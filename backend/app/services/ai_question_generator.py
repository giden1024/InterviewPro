import openai
import json
import logging
from typing import List, Dict, Any, Optional
from flask import current_app
from app.models.question import QuestionType, QuestionDifficulty, InterviewType
from app.models.resume import Resume
import os

logger = logging.getLogger(__name__)

class AIQuestionGenerator:
    """AI Question Generator for International Interview System"""
    
    def __init__(self):
        """Initialize AI question generator"""
        self.client = None
        self.model = "deepseek-chat"  # DeepSeek-V3 model
    
    def _get_client(self):
        """Lazy initialization of OpenAI client"""
        if self.client is None:
            try:
                api_key = current_app.config.get('DEEPSEEK_API_KEY')
                if not api_key:
                    logger.warning("DEEPSEEK_API_KEY not configured, using fallback questions only")
                    return None
                
                self.client = openai.OpenAI(
                    api_key=api_key,
                    base_url="https://api.deepseek.com"
                )
                logger.info("DeepSeek OpenAI client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
                return None
        
        return self.client
    
    def generate_questions_for_resume(
        self, 
        resume: Resume, 
        interview_type: InterviewType = InterviewType.COMPREHENSIVE,
        total_questions: int = 10,
        difficulty_distribution: Optional[Dict[str, int]] = None,
        type_distribution: Optional[Dict[str, int]] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate interview questions based on resume
        
        Args:
            resume: Resume object
            interview_type: Interview type
            total_questions: Total number of questions
            difficulty_distribution: Difficulty distribution
            type_distribution: Question type distribution
            
        Returns:
            List of generated questions
        """
        try:
            # Set default distributions
            if difficulty_distribution is None:
                difficulty_distribution = {"easy": 3, "medium": 5, "hard": 2}
            if type_distribution is None:
                type_distribution = self._get_default_type_distribution(interview_type)
            
            # Prepare resume context
            resume_context = self._prepare_resume_context(resume)
            
            # Generate questions
            questions = []
            
            # Generate questions by type and difficulty
            for question_type, count in type_distribution.items():
                for difficulty, diff_count in difficulty_distribution.items():
                    questions_needed = min(count, diff_count, total_questions - len(questions))
                    if questions_needed <= 0:
                        continue
                    
                    batch_questions = self._generate_questions_batch(
                        resume_context=resume_context,
                        question_type=QuestionType(question_type),
                        difficulty=QuestionDifficulty(difficulty),
                        count=questions_needed,
                        interview_type=interview_type
                    )
                    questions.extend(batch_questions)
                    
                    if len(questions) >= total_questions:
                        break
                
                if len(questions) >= total_questions:
                    break
            
            # Generate additional general questions if needed
            while len(questions) < total_questions:
                remaining = total_questions - len(questions)
                additional_questions = self._generate_questions_batch(
                    resume_context=resume_context,
                    question_type=QuestionType.GENERAL,
                    difficulty=QuestionDifficulty.MEDIUM,
                    count=remaining,
                    interview_type=interview_type
                )
                questions.extend(additional_questions[:remaining])
            
            return questions[:total_questions]
            
        except Exception as e:
            logger.error(f"Failed to generate questions: {e}")
            return self._get_fallback_questions(interview_type, total_questions)
    
    def _prepare_resume_context(self, resume: Resume) -> Dict[str, Any]:
        """Prepare resume context information"""
        return {
            'name': resume.name or 'Candidate',
            'skills': resume.skills or [],
            'experience': resume.experience or [],
            'education': resume.education or [],
            'summary': self._extract_summary_from_text(resume.raw_text)
        }
    
    def _extract_summary_from_text(self, text: str) -> str:
        """Extract summary from raw text"""
        if not text:
            return ""
        
        # Simple summary extraction: take first 500 characters
        summary = text.replace('\n', ' ').strip()
        return summary[:500] + "..." if len(summary) > 500 else summary
    
    def _get_default_type_distribution(self, interview_type: InterviewType) -> Dict[str, int]:
        """Get default question type distribution"""
        distributions = {
            InterviewType.TECHNICAL: {
                "technical": 6,
                "experience": 2,
                "situational": 2
            },
            InterviewType.HR: {
                "behavioral": 4,
                "experience": 3,
                "situational": 2,
                "general": 1
            },
            InterviewType.COMPREHENSIVE: {
                "technical": 3,
                "behavioral": 3,
                "experience": 2,
                "situational": 2
            }
        }
        return distributions.get(interview_type, distributions[InterviewType.COMPREHENSIVE])
    
    def _generate_questions_batch(
        self,
        resume_context: Dict[str, Any],
        question_type: QuestionType,
        difficulty: QuestionDifficulty,
        count: int,
        interview_type: InterviewType
    ) -> List[Dict[str, Any]]:
        """Generate a batch of questions with specified type and difficulty"""
        try:
            client = self._get_client()
            if not client:
                logger.info(f"AI client not available, using fallback questions for {question_type.value} {difficulty.value}")
                return self._get_fallback_questions_batch(question_type, difficulty, count)
            
            prompt = self._build_prompt(
                resume_context=resume_context,
                question_type=question_type,
                difficulty=difficulty,
                count=count,
                interview_type=interview_type
            )
            
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            return self._parse_ai_response(content, question_type, difficulty)
            
        except Exception as e:
            logger.error(f"AI question generation failed: {e}")
            return self._get_fallback_questions_batch(question_type, difficulty, count)
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for AI question generation"""
        return """You are a professional interview AI assistant that generates personalized interview questions based on candidate's resume information.

Please generate high-quality interview questions based on the provided resume information. Each question should:
1. Be based on the candidate's actual skills and experience
2. Match the specified question type and difficulty level
3. Have clear evaluation objectives
4. Include expected answer points
5. Be professional and appropriate for international candidates

Please return the questions in JSON format, with each question containing:
- question_text: Question content in English
- category: Question category (e.g., "Python", "Project Management", etc.)
- tags: List of relevant tags
- expected_answer: Key points expected in the answer
- evaluation_criteria: Evaluation criteria

Example format:
```json
{
  "questions": [
    {
      "question_text": "Can you describe how you handle exceptions in your Python projects?",
      "category": "Python",
      "tags": ["exception handling", "programming practices"],
      "expected_answer": "Should mention try-except blocks, specific exception types, logging, etc.",
      "evaluation_criteria": {
        "technical_accuracy": "Understanding of exception handling mechanisms",
        "practical_experience": "Evidence of real project experience",
        "best_practices": "Knowledge of best practices"
      }
    }
  ]
}
```

Important: 
- All questions and responses must be in English
- Questions should be culturally neutral and appropriate for international candidates
- Focus on technical competency and professional experience
- Avoid region-specific references or cultural assumptions"""
    
    def _build_prompt(
        self,
        resume_context: Dict[str, Any],
        question_type: QuestionType,
        difficulty: QuestionDifficulty,
        count: int,
        interview_type: InterviewType
    ) -> str:
        """Build AI prompt for question generation"""
        skills_str = ", ".join(resume_context['skills'][:10])  # Limit skills list length
        
        prompt = f"""Please generate {count} {question_type.value} type questions with {difficulty.value} difficulty level for the following candidate:

Candidate Information:
- Name: {resume_context['name']}
- Key Skills: {skills_str}
- Education Background: {len(resume_context['education'])} education entries
- Work Experience: {len(resume_context['experience'])} work experiences

Interview Type: {interview_type.value}

Requirements:
- Question Type: {question_type.value}
- Difficulty Level: {difficulty.value}
- Number of Questions: {count}

Please ensure questions are highly relevant to the candidate's skills and experience, and match the specified difficulty level.

Question Type Explanations:
- technical: Technical implementation, programming, tool usage, and other technical questions
- behavioral: Behavioral performance, teamwork, problem-solving approaches, etc.
- experience: Specific project experience and work history related questions
- situational: Response strategies in hypothetical scenarios
- general: General interview questions

Difficulty Explanations:
- easy: Basic concepts, simple applications
- medium: Practical applications, problem solving
- hard: Deep understanding, complex scenarios, architectural design
"""

        # Add specific skills and experience context
        if resume_context['skills']:
            prompt += f"\n\nKey Technical Skills: {', '.join(resume_context['skills'][:5])}"
        
        if resume_context['experience']:
            exp_summary = []
            for exp in resume_context['experience'][:3]:
                if isinstance(exp, dict):
                    title = exp.get('title', 'Position')
                    company = exp.get('company', 'Company')
                    exp_summary.append(f"{title} @ {company}")
            if exp_summary:
                prompt += f"\nMain Work Experience: {'; '.join(exp_summary)}"
        
        prompt += "\n\nPlease ensure you return valid JSON format. All content must be in English."
        
        return prompt
    
    def _parse_ai_response(
        self, 
        content: str, 
        question_type: QuestionType, 
        difficulty: QuestionDifficulty
    ) -> List[Dict[str, Any]]:
        """Parse AI response and extract questions"""
        try:
            # Try to extract JSON
            start = content.find('{')
            end = content.rfind('}') + 1
            if start != -1 and end > start:
                json_str = content[start:end]
                data = json.loads(json_str)
                
                questions = data.get('questions', [])
                result = []
                
                for q in questions:
                    if 'question_text' in q:
                        question = {
                            'question_text': q['question_text'],
                            'question_type': question_type,
                            'difficulty': difficulty,
                            'category': q.get('category', ''),
                            'tags': q.get('tags', []),
                            'expected_answer': q.get('expected_answer', ''),
                            'evaluation_criteria': q.get('evaluation_criteria', {}),
                            'ai_context': {
                                'model': self.model,
                                'generated_at': 'timestamp_placeholder'
                            }
                        }
                        result.append(question)
                
                return result
                
        except Exception as e:
            logger.error(f"Failed to parse AI response: {e}, Content: {content[:200]}...")
        
        # Return fallback questions when parsing fails
        return self._get_fallback_questions_batch(question_type, difficulty, 1)
    
    def _get_fallback_questions_batch(
        self, 
        question_type: QuestionType, 
        difficulty: QuestionDifficulty, 
        count: int
    ) -> List[Dict[str, Any]]:
        """Get fallback questions for specific type and difficulty"""
        fallback_questions = {
            QuestionType.TECHNICAL: {
                QuestionDifficulty.EASY: [
                    "Can you briefly introduce the characteristics of your most familiar programming language?",
                    "What development tools have you used in your projects?",
                    "Please explain what version control is and which tools you have used."
                ],
                QuestionDifficulty.MEDIUM: [
                    "Please describe a technical challenge you encountered in a project and your solution.",
                    "How do you ensure code quality and project maintainability?",
                    "Please share your understanding of software architecture design."
                ],
                QuestionDifficulty.HARD: [
                    "Please design an architecture solution for a high-concurrency system.",
                    "How do you approach system performance optimization?",
                    "Please discuss your understanding and practical experience with microservices architecture."
                ]
            },
            QuestionType.BEHAVIORAL: {
                QuestionDifficulty.EASY: [
                    "Please introduce your career goals.",
                    "What do you consider your main strengths?",
                    "How do you handle work pressure?"
                ],
                QuestionDifficulty.MEDIUM: [
                    "Please describe a situation where you disagreed with team members and how you resolved it.",
                    "How do you balance work quality with delivery deadlines?",
                    "Please describe your role and contributions in a team setting."
                ],
                QuestionDifficulty.HARD: [
                    "Please describe your experience leading a challenging project.",
                    "How do you drive project progress with limited resources?",
                    "Please share your views and experience on organizational culture change."
                ]
            },
            QuestionType.EXPERIENCE: {
                QuestionDifficulty.EASY: [
                    "Can you walk me through your most recent work experience?",
                    "What was your favorite project and why?",
                    "Describe a typical day in your previous role."
                ],
                QuestionDifficulty.MEDIUM: [
                    "Tell me about a project where you had to learn new technologies.",
                    "Describe a time when you had to work with a difficult stakeholder.",
                    "How did you handle a project that was behind schedule?"
                ],
                QuestionDifficulty.HARD: [
                    "Describe the most complex project you've managed from start to finish.",
                    "Tell me about a time you had to make a critical technical decision.",
                    "How did you handle a major system failure or crisis?"
                ]
            },
            QuestionType.SITUATIONAL: {
                QuestionDifficulty.EASY: [
                    "How would you prioritize tasks when everything seems urgent?",
                    "What would you do if you disagreed with your manager's approach?",
                    "How would you handle working with a remote team?"
                ],
                QuestionDifficulty.MEDIUM: [
                    "How would you approach debugging a complex system issue under time pressure?",
                    "What would you do if you discovered a security vulnerability in production?",
                    "How would you handle conflicting requirements from different stakeholders?"
                ],
                QuestionDifficulty.HARD: [
                    "How would you design a disaster recovery plan for a critical system?",
                    "What would you do if you had to migrate a legacy system with zero downtime?",
                    "How would you handle a situation where your team is consistently missing deadlines?"
                ]
            },
            QuestionType.GENERAL: {
                QuestionDifficulty.EASY: [
                    "Tell me about yourself and your professional background.",
                    "Why are you interested in this position?",
                    "What are your long-term career goals?"
                ],
                QuestionDifficulty.MEDIUM: [
                    "What motivates you in your work?",
                    "How do you stay updated with industry trends?",
                    "Describe your ideal work environment."
                ],
                QuestionDifficulty.HARD: [
                    "Where do you see yourself in 5 years and how does this role fit?",
                    "What would you do in your first 90 days in this role?",
                    "How do you handle failure and what have you learned from past failures?"
                ]
            }
        }
        
        questions_pool = fallback_questions.get(question_type, {}).get(difficulty, [
            "Please introduce your professional background and experience."
        ])
        
        result = []
        for i in range(min(count, len(questions_pool))):
            result.append({
                'question_text': questions_pool[i],
                'question_type': question_type,
                'difficulty': difficulty,
                'category': 'General',
                'tags': ['fallback'],
                'expected_answer': 'Answer based on personal experience',
                'evaluation_criteria': {'completeness': 'Completeness and logic of the answer'},
                'ai_context': {'source': 'fallback'}
            })
        
        return result
    
    def _get_fallback_questions(self, interview_type: InterviewType, total_questions: int) -> List[Dict[str, Any]]:
        """Get fallback question set when AI generation fails"""
        questions = []
        
        # Basic questions
        basic_questions = [
            {
                'question_text': 'Please introduce yourself briefly.',
                'question_type': QuestionType.GENERAL,
                'difficulty': QuestionDifficulty.EASY,
                'category': 'Introduction',
                'tags': ['self-introduction'],
                'expected_answer': 'Include educational background, work experience, skills, etc.',
                'evaluation_criteria': {'clarity': 'Clarity of expression', 'relevance': 'Content relevance'}
            },
            {
                'question_text': 'Why are you interested in this position?',
                'question_type': QuestionType.BEHAVIORAL,
                'difficulty': QuestionDifficulty.EASY,
                'category': 'Motivation',
                'tags': ['motivation', 'career'],
                'expected_answer': 'Combine personal interests with career planning',
                'evaluation_criteria': {'motivation': 'Clarity of motivation', 'alignment': 'Alignment with position'}
            },
            {
                'question_text': 'Please describe your most proud project experience.',
                'question_type': QuestionType.EXPERIENCE,
                'difficulty': QuestionDifficulty.MEDIUM,
                'category': 'Project',
                'tags': ['project', 'achievement'],
                'expected_answer': 'Include project background, personal responsibilities, achievements, etc.',
                'evaluation_criteria': {'impact': 'Project impact', 'contribution': 'Personal contribution'}
            },
            {
                'question_text': 'How do you handle challenging situations at work?',
                'question_type': QuestionType.SITUATIONAL,
                'difficulty': QuestionDifficulty.MEDIUM,
                'category': 'Problem Solving',
                'tags': ['problem-solving', 'resilience'],
                'expected_answer': 'Demonstrate problem-solving approach and resilience',
                'evaluation_criteria': {'approach': 'Problem-solving approach', 'adaptability': 'Adaptability'}
            },
            {
                'question_text': 'What are your main technical strengths?',
                'question_type': QuestionType.TECHNICAL,
                'difficulty': QuestionDifficulty.EASY,
                'category': 'Technical Skills',
                'tags': ['skills', 'technical'],
                'expected_answer': 'Highlight relevant technical skills and experience',
                'evaluation_criteria': {'relevance': 'Skill relevance', 'depth': 'Technical depth'}
            }
        ]
        
        # Repeat basic questions as needed
        while len(questions) < total_questions:
            for q in basic_questions:
                if len(questions) < total_questions:
                    questions.append(q.copy())
        
        return questions[:total_questions] 