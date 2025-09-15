from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

class Difficulty(str, Enum):
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"

class QuestionType(str, Enum):
    MCQ = "MCQ"
    TRUE_FALSE = "TRUE_FALSE"
    FILL_BLANK = "FILL_BLANK"

class Question(BaseModel):
    id: Optional[str] = None
    quiz_id: str
    type: QuestionType
    question: str
    options: List[str] = []  # For MCQ
    correct_answer: str
    explanation: str
    difficulty: Difficulty = Difficulty.MEDIUM
    topic: Optional[str] = None
    order: int
    created_at: Optional[datetime] = None

class Quiz(BaseModel):
    id: Optional[str] = None
    user_id: str
    title: str
    subject: str
    topic: Optional[str] = None
    description: Optional[str] = None
    time_limit: int  # in minutes
    difficulty: Difficulty = Difficulty.MEDIUM
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class QuizCreate(BaseModel):
    title: str
    subject: str
    topic: Optional[str] = None
    description: Optional[str] = None
    time_limit: int
    difficulty: Difficulty = Difficulty.MEDIUM
    num_questions: int
    question_types: List[QuestionType]
    content: Optional[str] = None

class QuizResponse(BaseModel):
    id: str
    user_id: str
    title: str
    subject: str
    topic: Optional[str] = None
    description: Optional[str] = None
    time_limit: int
    difficulty: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

class QuizSubmission(BaseModel):
    answers: List[dict]  # [{"questionId": "id", "answer": "answer", "timeSpent": 30}]
    time_spent: int  # in seconds

class QuizResult(BaseModel):
    id: Optional[str] = None
    user_id: str
    quiz_id: str
    score: int  # percentage
    total_time: int  # in seconds
    completed_at: Optional[datetime] = None

class QuizResultResponse(BaseModel):
    id: str
    user_id: str
    quiz_id: str
    score: int
    total_time: int
    completed_at: datetime

