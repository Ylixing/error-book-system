"""Grading endpoints"""

import logging
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import GradingRequest, GradingResponse, ErrorLogCreate, ErrorLogResponse
from app.models.database import (
    Question, StudentAnswer, ErrorLog, QuestionAnswer, StudentProfile
)
from app.services.ai_service import ai_service
from app.services.reminder_service import reminder_service
import os
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/grading", tags=["grading"])


@router.post("/submit-answer")
async def submit_answer(
    student_id: int,
    question_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Student submits answer image
    
    Args:
        student_id: Student profile ID
        question_id: Question ID
        file: Answer image file
        db: Database session
        
    Returns:
        Submission confirmation and grading results
    """
    try:
        # Validate student and question exist
        student = db.query(StudentProfile).filter(StudentProfile.id == student_id).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        question = db.query(Question).filter(Question.id == question_id).first()
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        
        # Save uploaded image
        if not os.path.exists("uploads"):
            os.makedirs("uploads")
        
        file_path = f"uploads/{student_id}_{question_id}_{datetime.utcnow().timestamp()}.jpg"
        with open(file_path, "wb") as f:
            f.write(await file.read())
        
        # Extract answer text using OCR
        extracted_text = ai_service.extract_answer_from_image(file_path)
        logger.info(f"Extracted text from image: {extracted_text}")
        
        # Save student answer
        student_answer = StudentAnswer(
            student_id=student_id,
            question_id=question_id,
            answer_image_url=file_path,
            extracted_text=extracted_text
        )
        db.add(student_answer)
        db.flush()
        
        # Grade the answer
        standard_answer_obj = db.query(QuestionAnswer).filter(
            QuestionAnswer.question_id == question_id
        ).first()
        
        if not standard_answer_obj:
            raise HTTPException(status_code=404, detail="Standard answer not found")
        
        grading_result = ai_service.grade_answer(
            student_answer=extracted_text,
            standard_answer=standard_answer_obj.answer_text,
            explanation=standard_answer_obj.explanation or "",
            knowledge_point=question.knowledge_point
        )
        
        # Save error log
        error_log = ErrorLog(
            student_id=student_id,
            student_answer_id=student_answer.id,
            question_id=question_id,
            is_correct=grading_result.get("is_correct", False),
            score=grading_result.get("score", 0.0),
            ai_feedback=grading_result.get("feedback", ""),
            ai_explanation=grading_result.get("ai_explanation", ""),
            error_analysis=grading_result.get("error_analysis"),
            error_count=1 if not grading_result.get("is_correct") else 0
        )
        db.add(error_log)
        db.commit()
        db.refresh(error_log)
        
        # Create review reminders if answer is wrong
        if not grading_result.get("is_correct"):
            reminder_service.create_review_reminders(db, error_log.id, student_id)
        
        return {
            "success": True,
            "student_answer_id": student_answer.id,
            "error_log_id": error_log.id,
            "grading_result": grading_result
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error submitting answer: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/results/{student_id}")
async def get_grading_results(
    student_id: int,
    homework_id: int = None,
    db: Session = Depends(get_db)
):
    """
    Get student's grading results
    
    Args:
        student_id: Student ID
        homework_id: Optional homework ID filter
        db: Database session
        
    Returns:
        List of grading results
    """
    try:
        query = db.query(ErrorLog).filter(ErrorLog.student_id == student_id)
        
        if homework_id:
            query = query.filter(
                ErrorLog.question_id.in_(
                    db.query(Question.id).filter(Question.homework_id == homework_id)
                )
            )
        
        results = query.all()
        return results
        
    except Exception as e:
        logger.error(f"Error getting grading results: {e}")
        raise HTTPException(status_code=500, detail=str(e))
