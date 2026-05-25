"""Review reminder endpoints"""

import logging
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.database import ReviewReminder, StudentProfile
from app.services.reminder_service import reminder_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/reminders", tags=["reminders"])


@router.get("/pending/{student_id}")
async def get_pending_reminders(
    student_id: int,
    db: Session = Depends(get_db)
):
    """
    Get pending reminders for a student
    
    Args:
        student_id: Student ID
        db: Database session
        
    Returns:
        List of pending reminders
    """
    try:
        student = db.query(StudentProfile).filter(StudentProfile.id == student_id).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        reminders = db.query(ReviewReminder).filter(
            ReviewReminder.student_id == student_id,
            ReviewReminder.is_sent == False,
            ReviewReminder.is_completed == False
        ).order_by(ReviewReminder.scheduled_date).all()
        
        return reminders
        
    except Exception as e:
        logger.error(f"Error getting pending reminders: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/mark-completed/{reminder_id}")
async def mark_reminder_completed(
    reminder_id: int,
    db: Session = Depends(get_db)
):
    """
    Mark a reminder as completed
    
    Args:
        reminder_id: Reminder ID
        db: Database session
        
    Returns:
        Success status
    """
    try:
        success = reminder_service.mark_reminder_completed(db, reminder_id)
        if not success:
            raise HTTPException(status_code=404, detail="Reminder not found")
        
        return {"success": True}
        
    except Exception as e:
        logger.error(f"Error marking reminder completed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
