from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from datetime import datetime
from . import models, schemas
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- User CRUD ---
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(
        email=user.email, 
        hashed_password=hashed_password, 
        username=user.username,
        full_name=user.full_name,
        age=user.age, 
        weight=user.weight, 
        height=user.height, 
        goals=user.goals
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user: models.User, user_update: schemas.UserUpdate):
    user_data = user_update.dict(exclude_unset=True)
    for key, value in user_data.items():
        setattr(user, key, value)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_all_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def update_user_role(db: Session, user_id: int, role: str):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        user.role = role
        db.commit()
        db.refresh(user)
    return user

def delete_user(db: Session, user_id: int):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
    return user

# --- Progress CRUD ---
def create_progress_entry(db: Session, progress: schemas.ProgressCreate, user_id: int):
    db_progress = models.Progress(**progress.dict(), owner_id=user_id)
    db.add(db_progress)
    db.commit()
    db.refresh(db_progress)
    return db_progress

def get_progress_entries_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Progress).filter(models.Progress.owner_id == user_id).order_by(models.Progress.date.desc()).offset(skip).limit(limit).all()

# --- Habit CRUD ---
def create_habit(db: Session, habit: schemas.HabitCreate, user_id: int):
    db_habit = models.Habit(**habit.dict(), owner_id=user_id)
    db.add(db_habit)
    db.commit()
    db.refresh(db_habit)
    return db_habit

def get_habits_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 30):
    return db.query(models.Habit).filter(models.Habit.owner_id == user_id).order_by(models.Habit.date.desc()).offset(skip).limit(limit).all()

# --- Meal Log CRUD ---
def create_meal_log(db: Session, meal_log: schemas.MealLogCreate, user_id: int):
    db_meal_log = models.MealLog(**meal_log.dict(), owner_id=user_id)
    db.add(db_meal_log)
    db.commit()
    db.refresh(db_meal_log)
    return db_meal_log

def get_meal_logs_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 30):
    return db.query(models.MealLog).filter(models.MealLog.owner_id == user_id).order_by(models.MealLog.date.desc()).offset(skip).limit(limit).all()

# --- Master Data CRUD (Exercises & Muscle Groups) ---

def get_exercise_by_name(db: Session, name: str):
    return db.query(models.Exercise).filter(models.Exercise.name == name).first()

def get_muscle_group_by_name(db: Session, name: str):
    return db.query(models.MuscleGroup).filter(models.MuscleGroup.name == name).first()

def get_exercises(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Exercise).offset(skip).limit(limit).all()

def get_muscle_groups(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.MuscleGroup).offset(skip).limit(limit).all()

def create_muscle_group(db: Session, muscle_group: schemas.MuscleGroupCreate):
    db_muscle_group = models.MuscleGroup(name=muscle_group.name)
    db.add(db_muscle_group)
    db.commit()
    db.refresh(db_muscle_group)
    return db_muscle_group

def create_exercise(db: Session, exercise: schemas.ExerciseCreate, user_id: Optional[int] = None):
    db_exercise = models.Exercise(name=exercise.name, description=exercise.description, created_by_user_id=user_id)
    for mg_id in exercise.muscle_group_ids:
        mg = db.query(models.MuscleGroup).filter(models.MuscleGroup.id == mg_id).first()
        if mg:
            db_exercise.muscle_groups.append(mg)
    db.add(db_exercise)
    db.commit()
    db.refresh(db_exercise)
    return db_exercise

# --- Detailed Workout Log CRUD ---

def create_workout_log(db: Session, workout_log: schemas.WorkoutLogCreate, user_id: int):
    db_workout_log = models.WorkoutLog(
        date=workout_log.date,
        name=workout_log.name,
        notes=workout_log.notes,
        owner_id=user_id
    )
    db.add(db_workout_log)
    
    for logged_exercise_in in workout_log.logged_exercises:
        db_logged_exercise = models.LoggedExercise(
            workout_log=db_workout_log,
            exercise_id=logged_exercise_in.exercise_id,
            notes=logged_exercise_in.notes
        )
        db.add(db_logged_exercise)
        
        for set_log_in in logged_exercise_in.sets:
            db_set_log = models.SetLog(
                logged_exercise=db_logged_exercise,
                set_number=set_log_in.set_number,
                reps=set_log_in.reps,
                weight=set_log_in.weight,
                weight_unit=set_log_in.weight_unit
            )
            db.add(db_set_log)
            
    db.commit()
    db.refresh(db_workout_log)
    return db_workout_log

def get_workout_log(db: Session, workout_log_id: int, user_id: int):
    return db.query(models.WorkoutLog).filter(models.WorkoutLog.id == workout_log_id, models.WorkoutLog.owner_id == user_id).first()

def get_workout_logs_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 10):
    return db.query(models.WorkoutLog).filter(models.WorkoutLog.owner_id == user_id).order_by(models.WorkoutLog.date.desc()).offset(skip).limit(limit).all()

def count_workouts_this_month(db: Session, user_id: int):
    from datetime import date, timedelta
    today = date.today()
    start_of_month = today.replace(day=1)
    return db.query(models.WorkoutLog).filter(
        models.WorkoutLog.owner_id == user_id,
        models.WorkoutLog.date >= start_of_month
    ).count()

# --- Workout Template CRUD ---
def create_workout_template(db: Session, template: schemas.WorkoutTemplateCreate, user_id: Optional[int] = None):
    db_template = models.WorkoutTemplate(
        name=template.name,
        description=template.description,
        color=template.color,
        created_by_user_id=user_id
    )
    db.add(db_template)
    
    for exercise_in in template.exercises:
        db_exercise = models.TemplateExercise(
            template=db_template,
            exercise_id=exercise_in.exercise_id,
            sets=exercise_in.sets,
            reps=exercise_in.reps,
            notes=exercise_in.notes
        )
        db.add(db_exercise)
    
    db.commit()
    db.refresh(db_template)
    return db_template

def get_workout_templates(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    # Fetch User's templates OR System templates (created_by_user_id is NULL)
    return db.query(models.WorkoutTemplate).filter(
        (models.WorkoutTemplate.created_by_user_id == user_id) | 
        (models.WorkoutTemplate.created_by_user_id == None)
    ).offset(skip).limit(limit).all()

# --- Challenges ---
def create_challenge(db: Session, challenge: schemas.ChallengeCreate):
    db_challenge = models.Challenge(**challenge.dict())
    db.add(db_challenge)
    db.commit()
    db.refresh(db_challenge)
    return db_challenge

def get_challenges(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Challenge).offset(skip).limit(limit).all()

from .ai import moderator
from .mind import models as mind_models

# --- Community Posts ---
async def create_post(db: Session, post: schemas.PostCreate, user_id: int):
    # Optimistic creation - save immediately
    db_post = models.Post(**post.dict(), user_id=user_id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

async def process_post_moderation(db: Session, post_id: int):
    # Background Task Logic
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        return

    # 1. Content Moderation
    is_safe, reason = await moderator.check_content(post.content)
    
    if not is_safe:
        # Log the violation
        log = mind_models.MonitoringLog(
            user_id=post.user_id,
            action=mind_models.MonitoringAction.WARNING,
            reason=f"Toxic: {reason} | Content: '{post.content[:50]}...'",
            timestamp=datetime.utcnow(),
            source="AI"
        )
        db.add(log)
        
        # Delete the toxic post
        db.delete(post)
        db.commit()
        # In a real app, we might push a notification to the user saying "Post removed"

def get_posts(db: Session, skip: int = 0, limit: int = 50):
    return db.query(models.Post).order_by(models.Post.created_at.desc()).offset(skip).limit(limit).all()

def delete_post(db: Session, post_id: int):
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if db_post:
        db.delete(db_post)
        db.commit()
    return db_post

def delete_challenge(db: Session, challenge_id: int):
    db_challenge = db.query(models.Challenge).filter(models.Challenge.id == challenge_id).first()
    if db_challenge:
        db.delete(db_challenge)
        db.commit()
    return db_challenge

# --- Analytics ---
def get_analytics_data(db: Session, user_id: int, request: schemas.AnalyticsRequest):
    query = db.query()
    
    group_label = None
    metric_calc = None
    
    # 1. Select Metric Calculation
    if request.metric == schemas.AnalyticsMetric.VOLUME:
        metric_calc = func.sum(models.SetLog.weight * models.SetLog.reps)
    elif request.metric == schemas.AnalyticsMetric.MAX_WEIGHT:
        metric_calc = func.max(models.SetLog.weight)
    elif request.metric == schemas.AnalyticsMetric.TOTAL_REPS:
        metric_calc = func.sum(models.SetLog.reps)
    elif request.metric == schemas.AnalyticsMetric.TOTAL_SETS:
        metric_calc = func.count(models.SetLog.id)
    elif request.metric == schemas.AnalyticsMetric.FREQUENCY:
        metric_calc = func.count(models.WorkoutLog.id.distinct())

    # 2. Build Query & Joins
    if request.metric == schemas.AnalyticsMetric.FREQUENCY:
        # Frequency: Count distinct workouts
        query = query.select_from(models.WorkoutLog)
        
        if request.group_by == schemas.AnalyticsGroupBy.MUSCLE_GROUP:
             query = query.join(models.LoggedExercise).join(models.Exercise).join(models.ExerciseMuscleGroupAssociation).join(models.MuscleGroup)
             group_label = models.MuscleGroup.name
             if request.filter_ids:
                query = query.filter(models.MuscleGroup.id.in_(request.filter_ids))
                
        elif request.group_by == schemas.AnalyticsGroupBy.EXERCISE:
             query = query.join(models.LoggedExercise).join(models.Exercise)
             group_label = models.Exercise.name
             if request.filter_ids:
                 query = query.filter(models.Exercise.id.in_(request.filter_ids))
                 
        elif request.group_by == schemas.AnalyticsGroupBy.WORKOUT_TEMPLATE:
             group_label = models.WorkoutLog.name
             
        elif request.group_by == schemas.AnalyticsGroupBy.DATE:
             group_label = models.WorkoutLog.date
             
    else:
        # Volume/Strength: Use SetLogs
        query = query.select_from(models.SetLog)
        query = query.join(models.LoggedExercise).join(models.WorkoutLog)
        
        if request.group_by == schemas.AnalyticsGroupBy.MUSCLE_GROUP:
             query = query.join(models.Exercise, models.LoggedExercise.exercise_id == models.Exercise.id)\
                          .join(models.ExerciseMuscleGroupAssociation)\
                          .join(models.MuscleGroup)
             group_label = models.MuscleGroup.name
             if request.filter_ids:
                 query = query.filter(models.MuscleGroup.id.in_(request.filter_ids))
                 
        elif request.group_by == schemas.AnalyticsGroupBy.EXERCISE:
             query = query.join(models.Exercise, models.LoggedExercise.exercise_id == models.Exercise.id)
             group_label = models.Exercise.name
             if request.filter_ids:
                 query = query.filter(models.Exercise.id.in_(request.filter_ids))
                 
        elif request.group_by == schemas.AnalyticsGroupBy.WORKOUT_TEMPLATE:
             group_label = models.WorkoutLog.name
             
        elif request.group_by == schemas.AnalyticsGroupBy.DATE:
             group_label = models.WorkoutLog.date

    # 3. Apply Common Filters
    query = query.filter(models.WorkoutLog.owner_id == user_id)
    if request.start_date:
        query = query.filter(models.WorkoutLog.date >= request.start_date)
    if request.end_date:
        query = query.filter(models.WorkoutLog.date <= request.end_date)
        
    # 4. Execute
    if group_label is not None:
        query = query.group_by(group_label)
        query = query.with_entities(group_label.label("label"), metric_calc.label("value"))
    else:
        query = query.with_entities(func.literal("Total").label("label"), metric_calc.label("value"))
        
    results = query.all()
    
    return [
        schemas.AnalyticsDataPoint(
            label=str(r.label) if r.label else "Unknown",
            value=float(r.value) if r.value else 0.0,
            date=str(r.label) if request.group_by == schemas.AnalyticsGroupBy.DATE and r.label else None
        )
        for r in results
    ]


# --- Dashboard Widgets ---
def create_widget(db: Session, widget: schemas.DashboardWidgetCreate, user_id: int):
    db_widget = models.DashboardWidget(**widget.model_dump(), user_id=user_id)
    db.add(db_widget)
    db.commit()
    db.refresh(db_widget)
    return db_widget

def get_widgets_by_user(db: Session, user_id: int):
    return db.query(models.DashboardWidget).filter(models.DashboardWidget.user_id == user_id).order_by(models.DashboardWidget.order).all()

def update_widget(db: Session, widget_id: int, widget_update: schemas.DashboardWidgetUpdate, user_id: int):
    db_widget = db.query(models.DashboardWidget).filter(models.DashboardWidget.id == widget_id, models.DashboardWidget.user_id == user_id).first()
    if not db_widget:
        return None
    
    update_data = widget_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_widget, key, value)
    
    db.commit()
    db.refresh(db_widget)
    return db_widget

def delete_widget(db: Session, widget_id: int, user_id: int):
    db_widget = db.query(models.DashboardWidget).filter(models.DashboardWidget.id == widget_id, models.DashboardWidget.user_id == user_id).first()
    if db_widget:
        db.delete(db_widget)
        db.commit()
        return True
    return False
