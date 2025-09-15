from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class SummaryType(str, Enum):
    BULLET = "BULLET"
    PARAGRAPH = "PARAGRAPH"
    DETAILED = "DETAILED"

class Summary(BaseModel):
    id: Optional[str] = None
    user_id: str
    title: str
    original_text: str
    summary_text: str
    original_length: int
    summary_length: int
    language: str = "english"
    type: SummaryType = SummaryType.BULLET
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class SummaryCreate(BaseModel):
    original_text: str
    type: SummaryType = SummaryType.BULLET
    language: str = "english"
    title: Optional[str] = None

class SummaryUpdate(BaseModel):
    title: Optional[str] = None
    summary_text: Optional[str] = None

class SummaryResponse(BaseModel):
    id: str
    user_id: str
    title: str
    original_text: str
    summary_text: str
    original_length: int
    summary_length: int
    language: str
    type: str
    created_at: datetime
    updated_at: datetime

