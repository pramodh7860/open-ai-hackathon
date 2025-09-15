from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class Priority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class TaskStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class StudyTask(BaseModel):
    id: Optional[str] = None
    user_id: str
    subject: str
    topic: str
    description: Optional[str] = None
    duration: int  # in minutes
    priority: Priority = Priority.MEDIUM
    date: datetime
    time: str  # HH:MM format
    status: TaskStatus = TaskStatus.PENDING
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class StudyTaskCreate(BaseModel):
    subject: str
    topic: str
    description: Optional[str] = None
    duration: int
    priority: Priority = Priority.MEDIUM
    date: datetime
    time: str

class StudyTaskUpdate(BaseModel):
    subject: Optional[str] = None
    topic: Optional[str] = None
    description: Optional[str] = None
    duration: Optional[int] = None
    priority: Optional[Priority] = None
    date: Optional[datetime] = None
    time: Optional[str] = None
    status: Optional[TaskStatus] = None

class StudyTaskResponse(BaseModel):
    id: str
    user_id: str
    subject: str
    topic: str
    description: Optional[str] = None
    duration: int
    priority: str
    date: datetime
    time: str
    status: str
    created_at: datetime
    updated_at: datetime

