"""
Mock email service for background task demonstration
"""
import logging
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger("fastapi_todo.email")

def send_todo_created_email(user_email: str, todo_title: str, todo_ddl: str | None) -> None:
    """
    Mock email sending function - in production this would use SMTP or email service
    """
    try:
        # Simulate email sending delay
        import time
        time.sleep(0.1)  # Simulate network latency
        
        # Mock email content
        email_content = f"""
        To: {user_email}
        Subject: New Todo Created Successfully
        
        Hello,
        
        Your new todo "{todo_title}" has been created successfully.
        
        Deadline: {todo_ddl or 'No deadline set'}
        Created at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        Best regards,
        FastAPI Todo App
        """
        
        # Log the "sent" email (in production, this would actually send via SMTP)
        logger.info(f"Mock email sent to {user_email} for todo '{todo_title}'")
        logger.debug(f"Email content: {email_content.strip()}")
        
    except Exception as e:
        logger.error(f"Failed to send email notification: {e}")
        # In production, you might want to retry or queue for later

def send_todo_updated_email(user_email: str, todo_title: str, changes: Dict[str, Any]) -> None:
    """
    Mock email for todo updates
    """
    try:
        import time
        time.sleep(0.1)
        
        changes_text = ", ".join([f"{k}: {v}" for k, v in changes.items()])
        
        logger.info(f"Mock update email sent to {user_email} for todo '{todo_title}'")
        logger.debug(f"Changes: {changes_text}")
        
    except Exception as e:
        logger.error(f"Failed to send update email: {e}")

def send_todo_deleted_email(user_email: str, todo_title: str) -> None:
    """
    Mock email for todo deletion
    """
    try:
        import time
        time.sleep(0.1)
        
        logger.info(f"Mock deletion email sent to {user_email} for todo '{todo_title}'")
        
    except Exception as e:
        logger.error(f"Failed to send deletion email: {e}")
