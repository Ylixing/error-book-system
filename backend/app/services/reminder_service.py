"""Reminder Service for scheduling review reminders based on Ebbinghaus curve"""

import logging
from datetime import datetime, timedelta
from typing import List
from sqlalchemy.orm import Session
from app.models.database import ReviewReminder, ErrorLog

logger = logging.getLogger(__name__)

# Ebbinghaus forgetting curve intervals (in days)
REVIEW_INTERVALS = [
    (1, "day1"),
    (3, "day3"),
    (7, "day7"),
    (14, "day14"),
    (30, "day30")
]


class ReminderService:
    """Service for managing review reminders"""
    
    @staticmethod
    def create_review_reminders(db: Session, error_log_id: int, student_id: int) -> List[ReviewReminder]:
        """
        Create review reminders for an error using Ebbinghaus curve
        
        Args:
            db: Database session
            error_log_id: ID of the error log
            student_id: ID of the student
            
        Returns:
            List of created reminders
        """
        try:
            reminders = []
            error_log = db.query(ErrorLog).filter(ErrorLog.id == error_log_id).first()
            
            if not error_log:
                logger.error(f"Error log {error_log_id} not found")
                return reminders
            
            for days, reminder_type in REVIEW_INTERVALS:
                scheduled_date = datetime.utcnow() + timedelta(days=days)
                
                reminder = ReviewReminder(
                    student_id=student_id,
                    error_id=error_log_id,
                    reminder_type=reminder_type,
                    scheduled_date=scheduled_date
                )
                
                db.add(reminder)
                reminders.append(reminder)
            
            db.commit()
            logger.info(f"Created {len(reminders)} review reminders for error {error_log_id}")
            return reminders
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating review reminders: {e}")
            raise
    
    @staticmethod
    def get_pending_reminders(db: Session, days_ahead: int = 1) -> List[ReviewReminder]:
        """
        Get reminders that need to be sent
        
        Args:
            db: Database session
            days_ahead: Number of days to look ahead (default 1)
            
        Returns:
            List of pending reminders
        """
        try:
            now = datetime.utcnow()
            future = now + timedelta(days=days_ahead)
            
            reminders = db.query(ReviewReminder).filter(
                ReviewReminder.is_sent == False,
                ReviewReminder.scheduled_date <= future,
                ReviewReminder.scheduled_date >= now
            ).all()
            
            return reminders
            
        except Exception as e:
            logger.error(f"Error getting pending reminders: {e}")
            raise
    
    @staticmethod
    def mark_reminder_as_sent(db: Session, reminder_id: int) -> bool:
        """
        Mark a reminder as sent
        
        Args:
            db: Database session
            reminder_id: ID of the reminder
            
        Returns:
            True if successful
        """
        try:
            reminder = db.query(ReviewReminder).filter(ReviewReminder.id == reminder_id).first()
            
            if reminder:
                reminder.is_sent = True
                reminder.sent_date = datetime.utcnow()
                db.commit()
                logger.info(f"Marked reminder {reminder_id} as sent")
                return True
            
            return False
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error marking reminder as sent: {e}")
            raise
    
    @staticmethod
    def mark_reminder_completed(db: Session, reminder_id: int) -> bool:
        """
        Mark a reminder as completed (student reviewed)
        
        Args:
            db: Database session
            reminder_id: ID of the reminder
            
        Returns:
            True if successful
        """
        try:
            reminder = db.query(ReviewReminder).filter(ReviewReminder.id == reminder_id).first()
            
            if reminder:
                reminder.is_completed = True
                db.commit()
                logger.info(f"Marked reminder {reminder_id} as completed")
                return True
            
            return False
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error marking reminder as completed: {e}")
            raise


reminder_service = ReminderService()
