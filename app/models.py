from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class UserRegister(BaseModel):
    name: str = Field(..., min_length=2, max_length=60)
    email: str = Field(..., min_length=3)
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    current_streak: int
    total_study_time: int

class AuthResponse(BaseModel):
    token: str
    user: UserResponse

class TopicCreate(BaseModel):
    subject: str
    topic_name: str
    difficulty_preference: Optional[str] = "Intermediate"

class StartSessionRequest(BaseModel):
    topic_id: int

class SubmitAnswerRequest(BaseModel):
    session_id: int
    concept_id: str
    question_id: str
    selected_option_index: Optional[int] = None
    response_time_seconds: float
    attempts: int = 1
    hints_used: int = 0
    skipped: bool = False
    time_since_last_action: float = 0.0

class RequestHintRequest(BaseModel):
    session_id: int
    concept_id: str
    question_id: str
    hint_tier: int = 1  # 1: Small hint, 2: Detailed hint, 3: Explanation / Worked Example

class CheckMasteryRequest(BaseModel):
    session_id: int

class BehavioralSignals(BaseModel):
    response_time_seconds: float
    accuracy: float
    attempts: int
    hints_used: int
    skipped: bool
    question_difficulty: str
    recent_performance: float
    repeated_mistakes: int
    time_since_last_action: float
