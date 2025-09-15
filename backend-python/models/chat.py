from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

class MessageType(str, Enum):
    USER = "USER"
    BOT = "BOT"

class ChatSession(BaseModel):
    id: Optional[str] = None
    user_id: str
    title: str
    subject: str = "general"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class ChatMessage(BaseModel):
    id: Optional[str] = None
    session_id: str
    type: MessageType
    content: str
    subject: Optional[str] = None
    helpful: Optional[bool] = None
    attachments: List[str] = []  # URLs to uploaded files
    created_at: Optional[datetime] = None

class ChatSessionCreate(BaseModel):
    title: str
    subject: str = "general"

class ChatMessageCreate(BaseModel):
    content: str
    subject: Optional[str] = None
    attachments: List[str] = []

class ChatMessageRate(BaseModel):
    helpful: bool

class ChatSessionResponse(BaseModel):
    id: str
    user_id: str
    title: str
    subject: str
    created_at: datetime
    updated_at: datetime

class ChatMessageResponse(BaseModel):
    id: str
    session_id: str
    type: str
    content: str
    subject: Optional[str] = None
    helpful: Optional[bool] = None
    attachments: List[str] = []
    created_at: datetime

