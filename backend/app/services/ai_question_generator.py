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
            
            # 🚀 性能优化：一次性生成所有问题，而不是多次调用AI API
            questions = self._generate_all_questions_at_once(
                resume_context=resume_context,
                interview_type=interview_type,
                total_questions=total_questions,
                difficulty_distribution=difficulty_distribution,
                type_distribution=type_distribution
            )
            
            return questions[:total_questions]
            
        except Exception as e:
            logger.error(f"Failed to generate questions: {e}")
            return self._get_fallback_questions(interview_type, total_questions)
    
    def _generate_all_questions_at_once(
        self,
        resume_context: Dict[str, Any],
        interview_type: InterviewType,
        total_questions: int,
        difficulty_distribution: Dict[str, int],
        type_distribution: Dict[str, int]
    ) -> List[Dict[str, Any]]:
        """一次性生成所有问题，避免多次AI API调用"""
        try:
            client = self._get_client()
            if not client:
                logger.info("AI client not available, using fallback questions")
                return self._get_fallback_questions(interview_type, total_questions)
            
            # 构建一次性生成所有问题的prompt
            prompt = self._build_comprehensive_prompt(
                resume_context=resume_context,
                interview_type=interview_type,
                total_questions=total_questions,
                difficulty_distribution=difficulty_distribution,
                type_distribution=type_distribution
            )
            
            # 一次AI调用生成所有问题
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_comprehensive_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=4000  # 增加token限制以容纳更多问题
            )
            
            content = response.choices[0].message.content
            questions = self._parse_comprehensive_ai_response(
                content, 
                type_distribution, 
                difficulty_distribution
            )
            
            # 如果AI生成的问题不足，用fallback补充
            if len(questions) < total_questions:
                logger.warning(f"AI generated {len(questions)} questions, need {total_questions}, using fallback for remaining")
                fallback_questions = self._get_fallback_questions(interview_type, total_questions - len(questions))
                questions.extend(fallback_questions)
            
            return questions
            
        except Exception as e:
            logger.error(f"Comprehensive AI question generation failed: {e}")
            return self._get_fallback_questions(interview_type, total_questions)
    
    def _build_comprehensive_prompt(
        self,
        resume_context: Dict[str, Any],
        interview_type: InterviewType,
        total_questions: int,
        difficulty_distribution: Dict[str, int],
        type_distribution: Dict[str, int]
    ) -> str:
        """构建一次性生成所有问题的comprehensive prompt"""
        skills_str = ", ".join(resume_context['skills'][:10])
        
        # 构建问题需求描述
        type_requirements = []
        for q_type, count in type_distribution.items():
            type_requirements.append(f"- {q_type}: {count} questions")
        
        difficulty_requirements = []
        for difficulty, count in difficulty_distribution.items():
            difficulty_requirements.append(f"- {difficulty}: {count} questions")
        
        prompt = f"""Please generate exactly {total_questions} interview questions for the following candidate in one comprehensive response:

Candidate Information:
- Name: {resume_context['name']}
- Key Skills: {skills_str}
- Education Background: {len(resume_context['education'])} education entries
- Work Experience: {len(resume_context['experience'])} work experiences

Interview Type: {interview_type.value}

Question Type Distribution:
{chr(10).join(type_requirements)}

Difficulty Distribution:
{chr(10).join(difficulty_requirements)}

IMPORTANT: Please generate exactly {total_questions} questions that match the specified distributions. Each question should be unique and relevant to the candidate's background."""
        
        # Add specific skills and experience context
        if resume_context['skills']:
            prompt += f"\n\nKey Technical Skills to focus on: {', '.join(resume_context['skills'][:5])}"
        
        if resume_context['experience']:
            exp_summary = []
            for exp in resume_context['experience'][:3]:
                if isinstance(exp, dict):
                    title = exp.get('title', 'Position')
                    company = exp.get('company', 'Company')
                    exp_summary.append(f"{title} @ {company}")
            if exp_summary:
                prompt += f"\nMain Work Experience: {'; '.join(exp_summary)}"
        
        prompt += f"\n\nPlease return exactly {total_questions} questions in valid JSON format. All content must be in English."
        
        return prompt
    
    def _get_comprehensive_system_prompt(self) -> str:
        """获取一次性生成所有问题的系统prompt"""
        return """You are a professional interview AI assistant that generates comprehensive sets of personalized interview questions based on candidate's resume information.

Please generate a complete set of interview questions based on the provided requirements. Each question should:
1. Be based on the candidate's actual skills and experience
2. Match the specified question type and difficulty level
3. Have clear evaluation objectives
4. Include expected answer points
5. Be professional and appropriate for international candidates

Please return ALL questions in a single JSON response with the following format:
```json
{
  "questions": [
    {
      "question_text": "Can you describe how you handle exceptions in your Python projects?",
      "question_type": "technical",
      "difficulty": "medium",
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

Important: 
- Generate exactly the requested number of questions
- All questions and responses must be in English
- Questions should be culturally neutral and appropriate for international candidates
- Focus on technical competency and professional experience
- Ensure variety in question types and difficulties as specified"""
    
    def _parse_comprehensive_ai_response(
        self, 
        content: str, 
        type_distribution: Dict[str, int],
        difficulty_distribution: Dict[str, int]
    ) -> List[Dict[str, Any]]:
        """解析一次性生成的AI响应"""
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
                        # 确保question_type和difficulty是正确的枚举类型
                        question_type = q.get('question_type', 'general')
                        difficulty = q.get('difficulty', 'medium')
                        
                        # 转换为枚举类型
                        try:
                            q_type_enum = QuestionType(question_type)
                        except ValueError:
                            q_type_enum = QuestionType.GENERAL
                        
                        try:
                            difficulty_enum = QuestionDifficulty(difficulty)
                        except ValueError:
                            difficulty_enum = QuestionDifficulty.MEDIUM
                        
                        question = {
                            'question_text': q['question_text'],
                            'question_type': q_type_enum,
                            'difficulty': difficulty_enum,
                            'category': q.get('category', ''),
                            'tags': q.get('tags', []),
                            'expected_answer': q.get('expected_answer', ''),
                            'evaluation_criteria': q.get('evaluation_criteria', {}),
                            'ai_context': {
                                'model': self.model,
                                'generated_at': 'timestamp_placeholder',
                                'generation_method': 'comprehensive_single_call'
                            }
                        }
                        result.append(question)
                
                logger.info(f"Successfully parsed {len(result)} questions from AI response")
                return result
                
        except Exception as e:
            logger.error(f"Failed to parse comprehensive AI response: {e}, Content: {content[:200]}...")
        
        # Return empty list if parsing fails - fallback will be used
        return []
    
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
    
    def generate_reference_answer(
        self,
        question: 'Question',
        resume: 'Resume',
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """实时生成问题的AI参考答案"""
        try:
            # 准备简历上下文
            resume_context = self._prepare_resume_context(resume)
            
            # 构建参考答案生成提示
            prompt = self._build_reference_answer_prompt(
                question=question,
                resume_context=resume_context,
                user_context=user_context or {}
            )
            
            # 调用AI生成参考答案
            client = self._get_client()
            if client:
                response = client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": self._get_reference_answer_system_prompt()},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=800,
                    temperature=0.7
                )
                
                content = response.choices[0].message.content.strip()
                return self._parse_reference_answer_response(content, question)
            else:
                # 返回fallback参考答案
                logger.warning("AI client not available, using fallback reference answer")
                return self._get_fallback_reference_answer(question)
                
        except Exception as e:
            logger.error(f"Failed to generate reference answer: {e}")
            return self._get_fallback_reference_answer(question)
    
    def _get_reference_answer_system_prompt(self) -> str:
        """获取参考答案生成的系统提示"""
        return """You are an expert interview coach helping candidates prepare for interviews. 
Your task is to generate high-quality, specific reference answers for interview questions based on the candidate's resume and the specific question.

Guidelines for reference answers:
1. Generate a COMPLETE, specific sample answer that the candidate can use as a template
2. Base the answer on the candidate's actual skills and experience from their resume
3. Make the answer realistic and authentic to the candidate's background
4. Include specific examples, technologies, and scenarios from their experience
5. Structure the answer professionally and logically
6. Keep answers practical, realistic, and interview-appropriate
7. Generate answers that sound natural and conversational

Response format should be JSON with:
- sample_answer: A complete, specific sample answer (2-3 paragraphs) that the candidate can adapt and use
- reference_answer: Additional guidance and tips for answering this type of question
- key_points: List of key points to cover
- structure_tips: Suggested answer structure
- example_scenarios: Relevant examples the candidate could mention
- dos_and_donts: Important dos and don'ts for this question type

The sample_answer should be the main focus - a complete, realistic answer that demonstrates exactly how to respond to this question using the candidate's background.

All content must be in English and professional."""

    def _build_reference_answer_prompt(
        self,
        question: 'Question',
        resume_context: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> str:
        """构建参考答案生成提示"""
        skills_str = ", ".join(resume_context['skills'][:8])
        
        prompt = f"""Generate a comprehensive reference answer for the following interview question:

Question: "{question.question_text}"
Question Type: {question.question_type.value}
Difficulty Level: {question.difficulty.value}
Category: {question.category}

Candidate Background:
- Name: {resume_context['name']}
- Key Skills: {skills_str}
- Education: {len(resume_context['education'])} education entries
- Work Experience: {len(resume_context['experience'])} work experiences

"""
        
        # 添加具体的技能和经验上下文
        if resume_context['skills']:
            prompt += f"Technical Skills: {', '.join(resume_context['skills'][:5])}\n"
        
        if resume_context['experience']:
            exp_summary = []
            for exp in resume_context['experience'][:2]:
                if isinstance(exp, dict):
                    title = exp.get('title', 'Position')
                    company = exp.get('company', 'Company')
                    exp_summary.append(f"{title} @ {company}")
            if exp_summary:
                prompt += f"Recent Experience: {'; '.join(exp_summary)}\n"
        
        # 添加问题特定的指导
        if question.question_type.value == 'technical':
            prompt += "\nFor this technical question, generate a sample answer that:\n- Demonstrates technical knowledge with specific examples\n- Shows problem-solving approach step by step\n- Includes best practices and real experience\n- Mentions specific technologies from the candidate's background\n- Provides a complete, realistic answer the candidate can adapt\n"
        elif question.question_type.value == 'behavioral':
            prompt += "\nFor this behavioral question, generate a sample answer that:\n- Uses STAR method (Situation, Task, Action, Result) structure\n- Provides a specific, realistic scenario from their background\n- Shows soft skills and teamwork in action\n- Demonstrates growth mindset and learning\n- Gives a complete story with clear outcome\n"
        elif question.question_type.value == 'experience':
            prompt += "\nFor this experience question, generate a sample answer that:\n- Highlights specific projects and achievements\n- Shows progression and growth in their career\n- Quantifies achievements with realistic metrics\n- Connects experience directly to the role\n- Provides concrete examples of their contributions\n"
        
        prompt += "\n\nIMPORTANT: Generate a complete, specific sample answer (2-3 paragraphs) that this candidate can use as a template. The sample answer should sound natural, authentic, and be based on their actual background. Include specific technologies, projects, or scenarios that align with their resume."
        
        return prompt
    
    def _parse_reference_answer_response(
        self,
        content: str,
        question: 'Question'
    ) -> Dict[str, Any]:
        """解析AI生成的参考答案响应"""
        try:
            # 尝试解析JSON格式
            start = content.find('{')
            end = content.rfind('}') + 1
            if start != -1 and end > start:
                json_str = content[start:end]
                data = json.loads(json_str)
                
                return {
                    'sample_answer': data.get('sample_answer', ''),
                    'reference_answer': data.get('reference_answer', ''),
                    'key_points': data.get('key_points', []),
                    'structure_tips': data.get('structure_tips', ''),
                    'example_scenarios': data.get('example_scenarios', []),
                    'dos_and_donts': data.get('dos_and_donts', {}),
                    'generated_by': 'ai',
                    'model': self.model,
                    'question_type': question.question_type.value,
                    'difficulty': question.difficulty.value
                }
        except Exception as e:
            logger.error(f"Failed to parse AI reference answer response: {e}")
        
        # 如果解析失败，返回简化的响应
        return {
            'sample_answer': content,
            'reference_answer': '',
            'key_points': [],
            'structure_tips': '',
            'example_scenarios': [],
            'dos_and_donts': {},
            'generated_by': 'ai_fallback',
            'model': self.model,
            'question_type': question.question_type.value,
            'difficulty': question.difficulty.value
        }
    
    def _get_fallback_reference_answer(self, question: 'Question') -> Dict[str, Any]:
        """获取fallback参考答案"""
        fallback_answers = {
            QuestionType.TECHNICAL: {
                'sample_answer': "I approach this by first understanding the core concept and requirements. For example, in my recent project using Python, I encountered a similar challenge where I needed to implement error handling for API calls. I used try-except blocks to catch specific exceptions, implemented proper logging to track issues, and added retry logic for transient failures. I also considered edge cases and made sure to follow best practices like not catching generic exceptions. This approach helped improve the application's reliability by 95% and made debugging much easier for the team.",
                'reference_answer': "For technical questions, structure your answer by first explaining the concept, then providing a practical example from your experience, and finally discussing best practices or potential challenges.",
                'key_points': [
                    "Start with clear concept explanation",
                    "Provide concrete examples from your projects",
                    "Discuss best practices and trade-offs",
                    "Show problem-solving approach"
                ],
                'structure_tips': "1. Define/Explain → 2. Example/Experience → 3. Best Practices → 4. Considerations",
                'example_scenarios': [
                    "Draw from your most relevant project experience",
                    "Mention specific technologies you've used",
                    "Discuss challenges you've overcome"
                ],
                'dos_and_donts': {
                    'dos': ["Be specific", "Show practical experience", "Explain your thinking"],
                    'donts': ["Give vague answers", "Pretend to know everything", "Skip examples"]
                }
            },
            QuestionType.BEHAVIORAL: {
                'sample_answer': "I'd like to share an experience from my previous role where I had to lead a team through a challenging deadline. The situation was that our client moved up their launch date by two weeks, which meant we had to deliver our software integration ahead of schedule. My task was to coordinate with a cross-functional team of 5 developers and ensure quality wasn't compromised. I organized daily standups, broke down the work into smaller sprints, and personally took on the most complex technical challenges to free up the team for parallel work. I also communicated regularly with stakeholders about our progress and any potential risks. As a result, we delivered the project on time with zero critical bugs, and the client was so impressed they extended our contract for the next phase. This experience taught me the importance of clear communication and adaptive leadership under pressure.",
                'reference_answer': "Use the STAR method (Situation, Task, Action, Result) to structure your behavioral answers. Start with a specific situation, explain your role and what needed to be done, describe the actions you took, and conclude with the positive results.",
                'key_points': [
                    "Use STAR method for structure",
                    "Choose relevant examples",
                    "Focus on your specific contributions",
                    "Highlight positive outcomes and learning"
                ],
                'structure_tips': "Situation → Task → Action → Result + Learning",
                'example_scenarios': [
                    "Team collaboration challenges",
                    "Project deadline pressures",
                    "Learning new technologies",
                    "Problem-solving situations"
                ],
                'dos_and_donts': {
                    'dos': ["Be specific", "Take ownership", "Show growth", "Quantify results"],
                    'donts': ["Blame others", "Be too general", "Focus only on team success"]
                }
            },
            QuestionType.EXPERIENCE: {
                'sample_answer': "In my role as a Software Developer at TechCorp, I led the development of a customer analytics dashboard that significantly improved our client's decision-making process. I was responsible for the full-stack development using React for the frontend and Python/Django for the backend, integrating with multiple data sources including PostgreSQL and third-party APIs. One of the biggest challenges was optimizing query performance for large datasets - I implemented database indexing and caching strategies that reduced load times from 30 seconds to under 3 seconds. I also worked closely with the UX team to ensure the interface was intuitive and collaborated with data scientists to implement meaningful visualizations. The project resulted in a 40% increase in user engagement and helped the client identify new revenue opportunities worth $2M annually. This experience strengthened my skills in performance optimization and cross-functional collaboration.",
                'reference_answer': "When discussing your experience, focus on projects and roles that directly relate to the position. Highlight your specific contributions, the technologies you used, challenges you overcame, and the impact of your work.",
                'key_points': [
                    "Choose most relevant experiences",
                    "Highlight specific contributions",
                    "Mention technologies and tools",
                    "Quantify impact and results"
                ],
                'structure_tips': "Context → Your Role → Actions Taken → Technologies Used → Results Achieved",
                'example_scenarios': [
                    "Most challenging project",
                    "Proudest achievement",
                    "Learning experience",
                    "Leadership opportunity"
                ],
                'dos_and_donts': {
                    'dos': ["Be specific", "Show progression", "Connect to role", "Mention metrics"],
                    'donts': ["Be too general", "Downplay your role", "Forget technical details"]
                }
            }
        }
        
        question_type = question.question_type
        if question_type in fallback_answers:
            answer_data = fallback_answers[question_type].copy()
        else:
            answer_data = {
                'sample_answer': "Structure your answer clearly, provide specific examples from your experience, and connect your response to the role requirements.",
                'reference_answer': "Structure your answer clearly, provide specific examples from your experience, and connect your response to the role requirements.",
                'key_points': ["Be specific", "Use examples", "Stay relevant", "Show enthusiasm"],
                'structure_tips': "Introduction → Main Points → Examples → Conclusion",
                'example_scenarios': ["Draw from your relevant experience"],
                'dos_and_donts': {
                    'dos': ["Be authentic", "Stay positive", "Ask questions"],
                    'donts': ["Be vague", "Speak negatively", "Seem disinterested"]
                }
            }
        
        answer_data.update({
            'generated_by': 'fallback',
            'question_type': question.question_type.value,
            'difficulty': question.difficulty.value
        })
        
        return answer_data 