from sqlalchemy.orm import Session
from .. import models, crud
from datetime import date, timedelta

def get_system_stats(db: Session):
    """
    Returns a dictionary ensuring critical system statistics for the Admin.
    """
    total_users = db.query(models.User).count()
    
    # Active users (logged a workout in last 7 days)
    seven_days_ago = date.today() - timedelta(days=7)
    active_users_count = db.query(models.WorkoutLog.owner_id).filter(models.WorkoutLog.date >= seven_days_ago).distinct().count()
    
    paid_users = db.query(models.User).filter(models.User.role == models.UserRole.PAID).count()
    trainers = db.query(models.User).filter(models.User.role == models.UserRole.TRAINER).count()
    admins = db.query(models.User).filter(models.User.role == models.UserRole.ADMIN).count()
    
    total_workouts = db.query(models.WorkoutLog).count()
    total_meals = db.query(models.MealLog).count()
    
    return {
        "user_stats": {
            "total_users": total_users,
            "active_users_7d": active_users_count,
            "paid_users": paid_users,
            "trainers": trainers,
            "admins": admins
        },
        "engagement_stats": {
            "total_workouts_logged": total_workouts,
            "total_meals_logged": total_meals
        },
        "system_status": "Operational",
        "last_updated": str(date.today())
    }
