from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum

class UserProvider(str, Enum):
    EMAIL = "email"
    GOOGLE = "google"

class User(BaseModel):
    id: Optional[str] = None
    email: EmailStr
    name: str
    avatar: Optional[str] = None
    provider: UserProvider = UserProvider.EMAIL
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str
    avatar: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class GoogleAuth(BaseModel):
    email: EmailStr
    name: str
    avatar: Optional[str] = None
    google_id: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    avatar: Optional[str] = None
    provider: str
    created_at: datetime

class UserProgress(BaseModel):
    id: Optional[str] = None
    user_id: str
    study_streak: int = 0
    total_hours: float = 0.0
    quizzes_completed: int = 0
    average_score: float = 0.0
    level: int = 1
    xp: int = 0
    last_active_date: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class Achievement(BaseModel):
    id: Optional[str] = None
    name: str
    description: str
    icon: str
    xp_reward: int = 0
    condition: str  # JSON string describing the condition
    created_at: Optional[datetime] = None

class UserAchievement(BaseModel):
    id: Optional[str] = None
    user_id: str
    achievement_id: str
    earned_at: Optional[datetime] = None

