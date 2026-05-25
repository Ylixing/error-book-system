"""Error book endpoints"""

import logging
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.database import ErrorLog, StudentProfile
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/errors", tags=["error-book"])


@router.get("/student/{student_id}")
async def get_student_errors(
    student_id: int,
    is_mastered: bool = False,
    db: Session = Depends(get_db)
):
    """
    Get student's error book
    
    Args:
        student_id: Student ID
        is_mastered: Filter by mastery status
        db: Database session
        
    Returns:
        List of error logs
    """
    try:
        student = db.query(StudentProfile).filter(StudentProfile.id == student_id).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        query = db.query(ErrorLog).filter(ErrorLog.student_id == student_id)
        
        if is_mastered is not None:
            query = query.filter(ErrorLog.is_mastered == is_mastered)
        
        errors = query.order_by(ErrorLog.last_error_date.desc()).all()
        
        return {
            "total_errors": len(errors),
            "errors": errors
        }
        
    except Exception as e:
        logger.error(f"Error getting student errors: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/mark-mastered/{error_id}")
async def mark_error_mastered(
    error_id: int,
    db: Session = Depends(get_db)
):
    """
    Mark an error as mastered
    
    Args:
        error_id: Error log ID
        db: Database session
        
    Returns:
        Updated error log
    """
    try:
        error = db.query(ErrorLog).filter(ErrorLog.id == error_id).first()
        if not error:
            raise HTTPException(status_code=404, detail="Error not found")
        
        error.is_mastered = True
        db.commit()
        db.refresh(error)
        
        return error
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error marking mastered: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics/{student_id}")
async def get_error_statistics(
    student_id: int,
    db: Session = Depends(get_db)
):
    """
    Get error statistics for a student
    
    Args:
        student_id: Student ID
        db: Database session
        
    Returns:
        Error statistics
    """
    try:
        errors = db.query(ErrorLog).filter(ErrorLog.student_id == student_id).all()
        
        total_errors = len(errors)
        mastered_errors = sum(1 for e in errors if e.is_mastered)
        unmastered_errors = total_errors - mastered_errors
        avg_error_count = sum(e.error_count for e in errors) / total_errors if total_errors > 0 else 0
        mastery_rate = (mastered_errors / total_errors * 100) if total_errors > 0 else 0
        
        return {
            "total_errors": total_errors,
            "mastered_errors": mastered_errors,
            "unmastered_errors": unmastered_errors,
            "avg_error_count": round(avg_error_count, 2),
            "mastery_rate": round(mastery_rate, 2)
        }
        
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))
