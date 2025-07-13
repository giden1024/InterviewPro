import openai
import logging
from flask import current_app

logger = logging.getLogger(__name__)

class SimpleAIResponder:
    """简化的AI回答生成器"""
    
    def __init__(self):
        self.client = None
        self.model = "deepseek-chat"
    
    def _get_client(self):
        """获取AI客户端"""
        if self.client is None:
            try:
                api_key = current_app.config.get('DEEPSEEK_API_KEY')
                if not api_key:
                    logger.warning("DEEPSEEK_API_KEY not configured")
                    return None
                
                self.client = openai.OpenAI(
                    api_key=api_key,
                    base_url="https://api.deepseek.com"
                )
                logger.info("DeepSeek AI client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize AI client: {e}")
                return None
        return self.client
    
    def generate_answer(self, question: str) -> str:
        """根据问题生成回答"""
        try:
            client = self._get_client()
            if not client:
                return self._get_fallback_answer(question)
            
            # 生成markdown格式的prompt
            prompt = f"Please provide a professional and well-structured answer to this interview question: {question}"
            
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": """You are a professional interview coach. Provide clear, structured answers to interview questions using markdown formatting. 

Follow this structure:
- Use **bold** for key points and important phrases
- Use bullet points (-) for lists
- Use > for important quotes or tips
- Use `code` formatting for technical terms or methods
- Keep responses practical and actionable
- Answer in 2-3 paragraphs maximum with proper markdown formatting

Example format:
## Key Points
- **Point 1**: Explanation with example
- **Point 2**: Another important aspect

> **Pro Tip**: Always include specific examples

Remember to format your response in clean markdown that will render well."""
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=600  # 稍微增加token限制以支持markdown格式
            )
            
            answer = response.choices[0].message.content.strip()
            logger.info(f"AI answer generated successfully for question: {question[:50]}...")
            return answer
            
        except Exception as e:
            logger.error(f"AI answer generation failed: {e}")
            return self._get_fallback_answer(question)
    
    def _get_fallback_answer(self, question: str) -> str:
        """AI不可用时的备用回答（markdown格式）"""
        # 根据问题关键词提供更有针对性的回答
        question_lower = question.lower()
        
        if any(word in question_lower for word in ['strength', 'strong', 'good at']):
            return """## Answering Strengths Questions

**Key Structure:**
- **Strength**: Choose one relevant to the role
- **Example**: Provide specific, measurable results  
- **Impact**: Show how it benefited your team/company
- **Application**: Connect to this position

> **Pro Tip**: Use the `STAR method` to structure your examples

**Remember**: Quantify your achievements whenever possible!"""
        
        elif any(word in question_lower for word in ['weakness', 'improve', 'challenge']):
            return """## Addressing Weaknesses

**Best Approach:**
- **Be Honest**: Choose a real weakness (not a disguised strength)
- **Show Awareness**: Demonstrate self-reflection
- **Action Plan**: Describe concrete improvement steps
- **Progress**: Share what you've already accomplished

> **Important**: Avoid weaknesses that directly impact core job requirements

**Example Structure**: "I used to struggle with X, so I Y, and now Z."""
        
        elif any(word in question_lower for word in ['why', 'motivation', 'interest']):
            return """## Showing Motivation & Interest

**Key Elements:**
- **Research**: Show you understand the company/role
- **Alignment**: Connect your goals to their mission
- **Personal Connection**: Explain what excites you
- **Long-term Vision**: Demonstrate career planning

> **Pro Tip**: Reference specific company initiatives or values

**Avoid**: Generic answers that could apply to any company"""
        
        elif any(word in question_lower for word in ['experience', 'project', 'example']):
            return """## Sharing Experience & Examples

**Use the STAR Method:**
- **Situation**: Set the context
- **Task**: Explain your responsibility
- **Action**: Detail what you did
- **Result**: Quantify the outcome

> **Remember**: Choose examples relevant to the target role

**Best Practices:**
- Use specific numbers and metrics
- Focus on your individual contribution
- Highlight transferable skills"""
        
        elif any(word in question_lower for word in ['future', 'goal', 'career']):
            return """## Discussing Career Goals

**Effective Strategy:**
- **Alignment**: Connect goals to company growth
- **Realistic Timeline**: Show practical planning
- **Mutual Benefit**: Explain value to employer
- **Flexibility**: Demonstrate adaptability

> **Key Point**: This role should be a logical next step

**Structure**: Short-term learning → Medium-term contribution → Long-term leadership"""
        
        else:
            return """## General Interview Answer Framework

**Universal Structure:**
- **Listen Carefully**: Understand what they're really asking
- **Structure Your Response**: Use frameworks like `STAR` or `PAR`
- **Be Specific**: Include concrete examples and metrics
- **Stay Relevant**: Connect to the role requirements

> **Pro Tip**: Practice your key stories beforehand

**Remember**: Show enthusiasm and ask thoughtful follow-up questions!""" 