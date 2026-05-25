"""SQLAlchemy Database Models"""

from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Boolean, ForeignKey, Table, JSON, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()


class User(Base):
    """用户表"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=True)
    phone = Column(String(20), nullable=True)
    openid = Column(String(100), unique=True, nullable=False)  # WeChat openid
    role = Column(String(20), default="teacher")  # teacher, student
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student_profiles = relationship("StudentProfile", back_populates="teacher")
    homeworks = relationship("Homework", back_populates="teacher")


class StudentProfile(Base):
    """学生资料表"""
    __tablename__ = "student_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    openid = Column(String(100), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    grade = Column(String(20), nullable=True)  # 初三、高二等
    subject = Column(String(50), default="Math")
    phone = Column(String(20), nullable=True)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    teacher = relationship("User", back_populates="student_profiles")
    student_answers = relationship("StudentAnswer", back_populates="student")
    error_logs = relationship("ErrorLog", back_populates="student")
    review_reminders = relationship("ReviewReminder", back_populates="student")
    grading_reports = relationship("GradingReport", back_populates="student")


class Homework(Base):
    """作业表"""
    __tablename__ = "homeworks"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subject = Column(String(50), default="Math")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    teacher = relationship("User", back_populates="homeworks")
    questions = relationship("Question", back_populates="homework")
    grading_reports = relationship("GradingReport", back_populates="homework")


class Question(Base):
    """题目表"""
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    homework_id = Column(Integer, ForeignKey("homeworks.id"), nullable=False)
    question_number = Column(Integer, nullable=True)
    question_text = Column(Text, nullable=False)
    difficulty = Column(String(20), nullable=True)  # easy, medium, hard
    knowledge_point = Column(String(200), nullable=True)
    max_score = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    homework = relationship("Homework", back_populates="questions")
    standard_answers = relationship("QuestionAnswer", back_populates="question")
    student_answers = relationship("StudentAnswer", back_populates="question")
    error_logs = relationship("ErrorLog", back_populates="question")


class QuestionAnswer(Base):
    """标准答案表"""
    __tablename__ = "question_answers"
    
    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    answer_text = Column(Text, nullable=False)  # 标准答案
    explanation = Column(Text, nullable=True)  # 详细解析
    key_points = Column(JSON, nullable=True)  # 关键点
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    question = relationship("Question", back_populates="standard_answers")


class StudentAnswer(Base):
    """学生答案表"""
    __tablename__ = "student_answers"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("student_profiles.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    answer_image_url = Column(String(500), nullable=False)  # 答案图片URL
    extracted_text = Column(Text, nullable=True)  # OCR提取的文字
    submitted_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    student = relationship("StudentProfile", back_populates="student_answers")
    question = relationship("Question", back_populates="student_answers")
    error_logs = relationship("ErrorLog", back_populates="student_answer")


class ErrorLog(Base):
    """错题记录表"""
    __tablename__ = "error_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("student_profiles.id"), nullable=False)
    student_answer_id = Column(Integer, ForeignKey("student_answers.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=True)
    is_correct = Column(Boolean, default=False)
    score = Column(Float, default=0.0)
    ai_feedback = Column(Text, nullable=True)  # AI批改意见
    ai_explanation = Column(Text, nullable=True)  # AI生成的解析
    error_analysis = Column(Text, nullable=True)  # 错误分析
    error_count = Column(Integer, default=1)  # 错误次数
    is_mastered = Column(Boolean, default=False)  # 是否已掌握
    first_error_date = Column(DateTime, default=datetime.utcnow)  # 第一次错误日期
    last_error_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 最后错误日期
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    student = relationship("StudentProfile", back_populates="error_logs")
    student_answer = relationship("StudentAnswer", back_populates="error_logs")
    question = relationship("Question", back_populates="error_logs")
    review_reminders = relationship("ReviewReminder", back_populates="error_log")


class ReviewReminder(Base):
    """复习提醒表（艾宾浩斯遗忘曲线）"""
    __tablename__ = "review_reminders"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("student_profiles.id"), nullable=False)
    error_id = Column(Integer, ForeignKey("error_logs.id"), nullable=False)
    reminder_type = Column(String(50), nullable=False)  # day1, day3, day7, day14, day30
    scheduled_date = Column(DateTime, nullable=False)  # 提醒日期
    is_sent = Column(Boolean, default=False)
    is_completed = Column(Boolean, default=False)
    sent_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    student = relationship("StudentProfile", back_populates="review_reminders")
    error_log = relationship("ErrorLog", back_populates="review_reminders")


class GradingReport(Base):
    """批改报告表"""
    __tablename__ = "grading_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("student_profiles.id"), nullable=False)
    homework_id = Column(Integer, ForeignKey("homeworks.id"), nullable=False)
    total_questions = Column(Integer, default=0)
    correct_questions = Column(Integer, default=0)
    error_questions = Column(Integer, default=0)
    accuracy_rate = Column(Float, default=0.0)  # 正确率
    total_score = Column(Float, default=0.0)
    max_score = Column(Float, default=0.0)
    report_data = Column(JSON, nullable=True)  # 详细报告数据
    generated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    student = relationship("StudentProfile", back_populates="grading_reports")
    homework = relationship("Homework", back_populates="grading_reports")
