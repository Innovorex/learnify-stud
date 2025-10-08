from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Optional

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    role: str

class LoginRequest(BaseModel):
    email: str
    password: str

class AssessmentCreate(BaseModel):
    teacher_id: int
    class_name: str
    subject: str
    chapter: str
    start_time: datetime
    end_time: datetime
    duration_minutes: int

class AssessmentOut(BaseModel):
    id: int
    class_name: str
    subject: str
    chapter: str
    start_time: datetime
    end_time: datetime
    duration_minutes: int

    class Config:
        from_attributes = True

class StudentAssessmentOut(BaseModel):
    id: int
    subject: str
    chapter: str
    start_time: datetime
    end_time: datetime
    duration_minutes: int

    class Config:
        from_attributes = True

class AnswerSubmission(BaseModel):
    student_id: int
    assessment_id: int
    answers: Dict[int, str]  # {question_id: "A"}

class ResultOut(BaseModel):
    id: int
    student_id: int
    assessment_id: int
    score: int
    submitted_at: datetime

    class Config:
        from_attributes = True

class StudentResultOut(BaseModel):
    assessment_id: int
    subject: str
    chapter: str
    score: int
    total: int
    submitted_at: datetime

class ClassPerformanceOut(BaseModel):
    assessment_id: int
    class_name: str
    average_score: float
    total_students: int
    top_scorer: Optional[str]
