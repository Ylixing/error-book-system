"""Pydantic schemas for request/response validation"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


# User Schemas
class UserBase(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    role: str = "teacher"


class UserCreate(UserBase):
    openid: str


class UserResponse(UserBase):
    id: int
    openid: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Student Profile Schemas
class StudentProfileBase(BaseModel):
    name: str
    grade: Optional[str] = None
    subject: str = "Math"
    phone: Optional[str] = None


class StudentProfileCreate(StudentProfileBase):
    openid: str
    teacher_id: int


class StudentProfileResponse(StudentProfileBase):
    id: int
    openid: str
    teacher_id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Question Schemas
class QuestionAnswerBase(BaseModel):
    answer_text: str
    explanation: Optional[str] = None
    key_points: Optional[List[str]] = None


class QuestionAnswerCreate(QuestionAnswerBase):
    pass


class QuestionAnswerResponse(QuestionAnswerBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class QuestionBase(BaseModel):
    question_number: Optional[int] = None
    question_text: str
    difficulty: Optional[str] = None
    knowledge_point: Optional[str] = None
    max_score: Optional[float] = 1.0


class QuestionCreate(QuestionBase):
    standard_answer: QuestionAnswerCreate


class QuestionResponse(QuestionBase):
    id: int
    homework_id: int
    standard_answers: List[QuestionAnswerResponse] = []
    created_at: datetime
    
    class Config:
        from_attributes = True


# Homework Schemas
class HomeworkBase(BaseModel):
    name: str
    description: Optional[str] = None
    subject: Optional[str] = "Math"


class HomeworkCreate(HomeworkBase):
    pass


class HomeworkResponse(HomeworkBase):
    id: int
    teacher_id: int
    created_at: datetime
    questions: List[QuestionResponse] = []
    
    class Config:
        from_attributes = True


# Student Answer Schemas
class StudentAnswerBase(BaseModel):
    answer_image_url: str
    extracted_text: Optional[str] = None


class StudentAnswerCreate(StudentAnswerBase):
    student_id: int
    question_id: int


class StudentAnswerResponse(StudentAnswerBase):
    id: int
    student_id: int
    question_id: int
    submitted_at: datetime
    
    class Config:
        from_attributes = True


# Error Log Schemas
class ErrorLogBase(BaseModel):
    is_correct: bool
    score: float
    ai_feedback: Optional[str] = None
    ai_explanation: Optional[str] = None
    error_analysis: Optional[str] = None


class ErrorLogCreate(ErrorLogBase):
    student_id: int
    student_answer_id: int
    question_id: Optional[int] = None


class ErrorLogResponse(ErrorLogBase):
    id: int
    student_id: int
    student_answer_id: int
    error_count: int
    is_mastered: bool
    first_error_date: datetime
    last_error_date: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


# Review Reminder Schemas
class ReviewReminderBase(BaseModel):
    reminder_type: str
    scheduled_date: datetime


class ReviewReminderCreate(ReviewReminderBase):
    student_id: int
    error_id: int


class ReviewReminderResponse(ReviewReminderBase):
    id: int
    student_id: int
    error_id: int
    is_sent: bool
    is_completed: bool
    sent_date: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Grading Report Schemas
class GradingReportResponse(BaseModel):
    id: int
    student_id: int
    homework_id: int
    total_questions: int
    correct_questions: int
    error_questions: int
    accuracy_rate: float
    total_score: float
    max_score: float
    generated_at: datetime
    
    class Config:
        from_attributes = True


# AI Grading Request/Response
class GradingRequest(BaseModel):
    student_id: int
    question_id: int
    answer_image_url: str
    extracted_answer_text: Optional[str] = None


class GradingResponse(BaseModel):
    is_correct: bool
    score: float
    feedback: str
    explanation: str
    error_analysis: Optional[str] = None
    suggestions: Optional[str] = None


# WeChat Authentication
class WeChatLoginRequest(BaseModel):
    code: str
    userInfo: Optional[dict] = None


class WeChatLoginResponse(BaseModel):
    access_token: str
    user_id: int
    openid: str
    user_type: str  # "teacher" or "student"
