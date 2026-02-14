from pydantic import BaseModel
from datetime import date, datetime
from typing import List, Optional, Union
from .models import UserRole
from enum import Enum

# --- Analytics Schemas ---
class AnalyticsMetric(str, Enum):
    VOLUME = "volume" # weight * reps * sets
    MAX_WEIGHT = "max_weight"
    TOTAL_REPS = "total_reps"
    TOTAL_SETS = "total_sets"
    FREQUENCY = "frequency" # number of workout sessions

class AnalyticsGroupBy(str, Enum):
    MUSCLE_GROUP = "muscle_group"
    EXERCISE = "exercise"
    WORKOUT_TEMPLATE = "workout_template"
    DATE = "date" # Over time
    
class AnalyticsRequest(BaseModel):
    metric: AnalyticsMetric
    group_by: AnalyticsGroupBy
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    filter_ids: List[int] = [] # Optional IDs to filter by (e.g. specific exercises or muscles)

class AnalyticsDataPoint(BaseModel):
    label: str # The group name (e.g., "Chest", "Bench Press", "2023-10-27")
    date: Optional[str] = None # For time-series data
    value: float

# --- Progress Schemas ---
class ProgressBase(BaseModel):
    date: date
    weight: float
    body_fat_percentage: Optional[float] = None
    photo_url: Optional[str] = None

class ProgressCreate(ProgressBase):
    pass

class Progress(ProgressBase):
    id: int
    owner_id: int
    class Config:
        from_attributes = True

# --- Habit Schemas ---
class HabitBase(BaseModel):
    date: date
    sleep_hours: Optional[float] = None
    water_liters: Optional[float] = None
    steps: Optional[int] = None
    daily_notes: Optional[str] = None

class HabitCreate(HabitBase):
    pass

class Habit(HabitBase):
    id: int
    owner_id: int
    class Config:
        from_attributes = True

# --- Meal Log Schemas ---
class MealLogBase(BaseModel):
    date: date
    meal_type: Optional[str] = None
    image_url: Optional[str] = None
    description: Optional[str] = None
    calories: Optional[int] = None
    protein_g: Optional[float] = None
    carbs_g: Optional[float] = None
    fats_g: Optional[float] = None

class MealLogCreate(MealLogBase):
    pass

class MealLog(MealLogBase):
    id: int
    owner_id: int
    class Config:
        from_attributes = True

# --- Chat Schema ---
class ChatMessage(BaseModel):
    role: str
    content: str

class WorkoutParseRequest(BaseModel):
    text: str

# --- Master Data Schemas ---
class MuscleGroupBase(BaseModel):
    name: str

class MuscleGroupCreate(MuscleGroupBase):
    pass

class MuscleGroup(MuscleGroupBase):
    id: int
    class Config:
        from_attributes = True

class ExerciseBase(BaseModel):
    name: str
    description: Optional[str] = None

class ExerciseCreate(ExerciseBase):
    muscle_group_ids: List[int] = []

class Exercise(ExerciseBase):
    id: int
    muscle_groups: List[MuscleGroup] = []
    class Config:
        from_attributes = True

# --- Detailed Workout Logging Schemas ---
class SetLogBase(BaseModel):
    set_number: int
    reps: int
    weight: float
    weight_unit: str = 'kg'

class SetLogCreate(SetLogBase):
    pass

class SetLog(SetLogBase):
    id: int
    class Config:
        from_attributes = True

class LoggedExerciseBase(BaseModel):
    exercise_id: int
    notes: Optional[str] = None

class LoggedExerciseCreate(LoggedExerciseBase):
    sets: List[SetLogCreate]

class LoggedExercise(LoggedExerciseBase):
    id: int
    exercise: Exercise
    sets: List[SetLog] = []
    class Config:
        from_attributes = True

class WorkoutLogBase(BaseModel):
    date: date
    name: str
    notes: Optional[str] = None

class WorkoutLogCreate(WorkoutLogBase):
    logged_exercises: List[LoggedExerciseCreate]

class WorkoutLog(WorkoutLogBase):
    id: int
    owner_id: int
    logged_exercises: List[LoggedExercise] = []
    class Config:
        from_attributes = True

# --- Core User Schemas ---
class UserBase(BaseModel):
    email: str
    username: Optional[str] = None
    full_name: Optional[str] = None
    age: Optional[int] = None
    weight: Optional[float] = None
    height: Optional[float] = None
    goals: Optional[str] = None
    profile_picture: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[str] = None
    age: Optional[int] = None
    weight: Optional[float] = None
    height: Optional[float] = None
    goals: Optional[str] = None
    profile_picture: Optional[str] = None

class User(UserBase):
    id: int
    role: UserRole
    class Config:
        from_attributes = True

class UserStats(BaseModel):
    workouts_this_month: int
    current_weight: Optional[float] = None
    total_progress: Optional[float] = None

# --- Workout Template Schemas ---
class TemplateExerciseBase(BaseModel):
    exercise_id: int
    sets: int = 3
    reps: int = 10
    notes: Optional[str] = None

class TemplateExerciseCreate(TemplateExerciseBase):
    pass

class TemplateExercise(TemplateExerciseBase):
    id: int
    exercise: Exercise
    class Config:
        from_attributes = True

class WorkoutTemplateBase(BaseModel):
    name: str
    description: Optional[str] = None
    color: str = "from-blue-500 to-cyan-400"

class WorkoutTemplateCreate(WorkoutTemplateBase):
    exercises: List[TemplateExerciseCreate]

class WorkoutTemplate(WorkoutTemplateBase):
    id: int
    creator: Optional[User] = None
    template_exercises: List[TemplateExercise] = []
    class Config:
        from_attributes = True

# --- Challenges ---
class ChallengeBase(BaseModel):
    title: str
    description: str
    start_date: date
    end_date: date
    color: Optional[str] = "from-orange-500 to-red-500"

class ChallengeCreate(ChallengeBase):
    pass

class Challenge(ChallengeBase):
    id: int
    participants_count: int

    class Config:
        from_attributes = True

# --- Community Posts ---
class PostBase(BaseModel):
    content: str

class PostCreate(PostBase):
    pass

class Post(PostBase):
    id: int
    user_id: int
    created_at: datetime
    likes: int
    author: Optional[User] = None

    class Config:
        from_attributes = True


# --- Dashboard Widgets ---
class DashboardWidgetBase(BaseModel):
    title: str
    metric: str
    group_by: str
    time_range: str
    chart_type: str = "area"
    filter_type: str = "none"
    filter_id: Optional[str] = None
    order: int = 0

class DashboardWidgetCreate(DashboardWidgetBase):
    pass

class DashboardWidgetUpdate(BaseModel):
    title: Optional[str] = None
    metric: Optional[str] = None
    group_by: Optional[str] = None
    time_range: Optional[str] = None
    chart_type: Optional[str] = None
    filter_type: Optional[str] = None
    filter_id: Optional[str] = None
    order: Optional[int] = None

class DashboardWidget(DashboardWidgetBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True

class AIInsightRequest(BaseModel):
    context: str
