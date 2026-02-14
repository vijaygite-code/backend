from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..core.database import get_db
from .. import models, schemas
from ..auth import auth

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)

@router.post("/missing-exercise", status_code=200)
def log_missing_exercise(
    exercise_name: str, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Logs a missing exercise reported by a user during workout logging.
    This can be stored in a database table or just logged to a file/console for now.
    For MVP, we'll just log it to console/text file, or create a simple 'AdminLog' entry if we had one.
    Let's just print it for now or return success, assuming admin checks system logs.
    Or better, let's create a textual log file.
    """
    # Ideally, save to DB. For now, append to a file.
    log_entry = f"User {current_user.username} ({current_user.id}) reported missing exercise: {exercise_name}\n"
    with open("missing_exercises.log", "a") as f:
        f.write(log_entry)
            
    return {"message": "Reported to admin"}
