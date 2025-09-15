import openai
import os
import json
import logging
from typing import List, Dict, Any
from models.summary import SummaryType
from models.quiz import QuestionType, Difficulty

logger = logging.getLogger(__name__)

# Initialize OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY")

class AIService:
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    async def generate_summary(
        self, 
        text: str, 
        summary_type: SummaryType, 
        language: str = "english"
    ) -> str:
        """Generate AI summary of text"""
        try:
            prompt = self._get_summary_prompt(text, summary_type, language)
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at creating clear, accurate, and helpful summaries. Always respond in the requested language and maintain the original meaning while making the content more accessible."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            return response.choices[0].message.content or "Unable to generate summary"
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return self._generate_fallback_summary(text, summary_type)
    
    async def generate_quiz_questions(
        self,
        content: str,
        subject: str,
        topic: str,
        num_questions: int,
        difficulty: Difficulty,
        question_types: List[QuestionType]
    ) -> List[Dict[str, Any]]:
        """Generate AI quiz questions"""
        try:
            prompt = self._get_quiz_prompt(
                content, subject, topic, num_questions, difficulty, question_types
            )
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert educator who creates high-quality quiz questions. Always provide accurate answers and clear explanations. Return only valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=2000,
                temperature=0.5
            )
            
            content = response.choices[0].message.content
            if not content:
                raise Exception("No content generated")
            
            # Parse JSON response
            questions = json.loads(content)
            return questions if isinstance(questions, list) else []
            
        except Exception as e:
            logger.error(f"OpenAI quiz generation error: {e}")
            return self._generate_fallback_questions(subject, topic, num_questions)
    
    async def generate_chat_response(
        self,
        message: str,
        subject: str,
        conversation_history: List[Dict[str, str]] = None
    ) -> str:
        """Generate AI chat response"""
        try:
            system_prompt = f"You are an AI study assistant specializing in {subject}. You help students understand concepts, solve problems, and learn effectively. Be encouraging, clear, and educational in your responses. If you don't know something, admit it and suggest how the student can find the answer."
            
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add conversation history
            if conversation_history:
                messages.extend(conversation_history[-10:])  # Keep last 10 messages
            
            messages.append({"role": "user", "content": message})
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=1000,
                temperature=0.7
            )
            
            return response.choices[0].message.content or "I apologize, but I cannot provide a response at this time."
            
        except Exception as e:
            logger.error(f"OpenAI chat error: {e}")
            return self._generate_fallback_chat_response(message, subject)
    
    def _get_summary_prompt(self, text: str, summary_type: SummaryType, language: str) -> str:
        """Get the appropriate prompt for summary generation"""
        if summary_type == SummaryType.BULLET:
            return f"Summarize the following text into clear, concise bullet points. Focus on the key concepts and main ideas. Language: {language}\n\nText: {text}"
        elif summary_type == SummaryType.PARAGRAPH:
            return f"Summarize the following text into a well-structured paragraph that captures the main ideas and key points. Language: {language}\n\nText: {text}"
        elif summary_type == SummaryType.DETAILED:
            return f"Provide a comprehensive summary of the following text, including main concepts, key details, and important insights. Language: {language}\n\nText: {text}"
        else:
            return f"Summarize the following text. Language: {language}\n\nText: {text}"
    
    def _get_quiz_prompt(
        self, 
        content: str, 
        subject: str, 
        topic: str, 
        num_questions: int, 
        difficulty: Difficulty, 
        question_types: List[QuestionType]
    ) -> str:
        """Get the appropriate prompt for quiz generation"""
        return f"""Generate {num_questions} quiz questions about {topic} in {subject}. 
        Difficulty: {difficulty}
        Question types: {', '.join(question_types)}
        
        Content to base questions on: {content}
        
        Return the questions in JSON format with this structure:
        [
            {{
                "type": "mcq",
                "question": "Question text",
                "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
                "correctAnswer": 0,
                "explanation": "Explanation of the answer",
                "difficulty": "easy",
                "topic": "Topic name"
            }}
        ]"""
    
    def _generate_fallback_summary(self, text: str, summary_type: SummaryType) -> str:
        """Generate a fallback summary when AI is unavailable"""
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        key_sentences = sentences[:5]  # Take first 5 sentences
        
        if summary_type == SummaryType.BULLET:
            return '\n'.join([f"• {sentence}" for sentence in key_sentences])
        elif summary_type == SummaryType.PARAGRAPH:
            return '. '.join(key_sentences) + '.'
        elif summary_type == SummaryType.DETAILED:
            return f"Summary:\n\n{'. '.join(key_sentences)}.\n\nKey points:\n" + '\n'.join([f"- {sentence}" for sentence in key_sentences])
        else:
            return '. '.join(key_sentences) + '.'
    
    def _generate_fallback_questions(self, subject: str, topic: str, num_questions: int) -> List[Dict[str, Any]]:
        """Generate fallback questions when AI is unavailable"""
        sample_questions = [
            {
                "type": "mcq",
                "question": f"What is the main concept of {topic} in {subject}?",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "correctAnswer": 0,
                "explanation": f"This is a sample question about {topic}.",
                "difficulty": "easy",
                "topic": topic,
            },
            {
                "type": "true-false",
                "question": f"{topic} is an important concept in {subject}.",
                "correctAnswer": "true",
                "explanation": f"This statement is generally true about {topic}.",
                "difficulty": "easy",
                "topic": topic,
            },
        ]
        
        return sample_questions[:num_questions]
    
    def _generate_fallback_chat_response(self, message: str, subject: str) -> str:
        """Generate fallback chat response when AI is unavailable"""
        responses = [
            f"That's a great question about {subject}! While I'd need more context to give you a complete answer, I'd recommend checking your textbook or asking your teacher for clarification.",
            f"I understand you're asking about {subject}. This is an important topic that requires careful study. Consider breaking it down into smaller parts to better understand it.",
            f"Thanks for your question! For {subject} topics like this, I'd suggest reviewing the fundamental concepts first, then building up to more complex ideas.",
        ]
        
        import random
        return random.choice(responses)

# Global AI service instance
ai_service = AIService()

