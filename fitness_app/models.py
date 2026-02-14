import enum
from sqlalchemy import Column, Integer, String, Float, Text, Date, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship
from datetime import date, datetime
from .core.database import Base

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    PAID = "paid"
    unpaid = "unpaid"
    TRAINER = "trainer"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True, nullable=True) # Nullable for existing users
    full_name = Column(String, nullable=True)
    hashed_password = Column(String)
    role = Column(Enum(UserRole), default=UserRole.unpaid, nullable=False)

    age = Column(Integer)
    weight = Column(Float)
    height = Column(Float)
    goals = Column(Text)
    profile_picture = Column(String, nullable=True)

    workout_logs = relationship("WorkoutLog", back_populates="owner")
    progress_entries = relationship("Progress", back_populates="owner")
    habit_entries = relationship("Habit", back_populates="owner")
    meal_logs = relationship("MealLog", back_populates="owner")

class Habit(Base):
    __tablename__ = "habits"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, index=True, default=date.today)
    sleep_hours = Column(Float, nullable=True)
    water_liters = Column(Float, nullable=True)
    steps = Column(Integer, nullable=True)
    daily_notes = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    owner = relationship("User", back_populates="habit_entries")

class MealLog(Base):
    __tablename__ = "meal_logs"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, index=True, default=date.today)
    meal_type = Column(String, nullable=True) # e.g., "Breakfast", "Lunch", "Snack"
    image_url = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    calories = Column(Integer, nullable=True)
    protein_g = Column(Float, nullable=True)
    carbs_g = Column(Float, nullable=True)
    fats_g = Column(Float, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    owner = relationship("User", back_populates="meal_logs")

class Progress(Base):
    __tablename__ = "progress"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, index=True, default=date.today)
    weight = Column(Float, nullable=False)
    body_fat_percentage = Column(Float, nullable=True)
    photo_url = Column(String, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="progress_entries")

class WorkoutLog(Base):
    __tablename__ = "workout_logs"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, index=True)
    name = Column(String)
    notes = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="workout_logs")
    logged_exercises = relationship("LoggedExercise", back_populates="workout_log", cascade="all, delete-orphan")

class LoggedExercise(Base):
    __tablename__ = "logged_exercises"
    id = Column(Integer, primary_key=True, index=True)
    workout_log_id = Column(Integer, ForeignKey("workout_logs.id"))
    exercise_id = Column(Integer, ForeignKey("exercises.id"))
    notes = Column(Text, nullable=True)

    workout_log = relationship("WorkoutLog", back_populates="logged_exercises")
    exercise = relationship("Exercise")
    sets = relationship("SetLog", back_populates="logged_exercise", cascade="all, delete-orphan")

class SetLog(Base):
    __tablename__ = "set_logs"
    id = Column(Integer, primary_key=True, index=True)
    logged_exercise_id = Column(Integer, ForeignKey("logged_exercises.id"))
    set_number = Column(Integer)
    reps = Column(Integer)
    weight = Column(Float)
    weight_unit = Column(String, default="kg")

    logged_exercise = relationship("LoggedExercise", back_populates="sets")

class Exercise(Base):
    __tablename__ = "exercises"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(Text, nullable=True)
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    muscle_groups = relationship("MuscleGroup", secondary="exercise_muscle_group_association")

class MuscleGroup(Base):
    __tablename__ = "muscle_groups"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

class ExerciseMuscleGroupAssociation(Base):
    __tablename__ = "exercise_muscle_group_association"
    exercise_id = Column(Integer, ForeignKey("exercises.id"), primary_key=True)
    muscle_group_id = Column(Integer, ForeignKey("muscle_groups.id"), primary_key=True)

class PasswordReset(Base):
    __tablename__ = "password_resets"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True)
    otp = Column(String)
    expires_at = Column(Date) # Should be DateTime in real app, using Date for consistency with other fields if SQLite limitation? No, SQLite supports DateTime.

class WorkoutTemplate(Base):
    __tablename__ = "workout_templates"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(Text, nullable=True)
    color = Column(String, default="from-blue-500 to-cyan-400")
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True) # Nullable for system templates if we want, or usually Admin

    creator = relationship("User")
    template_exercises = relationship("TemplateExercise", back_populates="template", cascade="all, delete-orphan")

class TemplateExercise(Base):
    __tablename__ = "template_exercises"
    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("workout_templates.id"))
    exercise_id = Column(Integer, ForeignKey("exercises.id"))
    sets = Column(Integer, default=3)
    reps = Column(Integer, default=10) # Target reps
    notes = Column(Text, nullable=True)

    template = relationship("WorkoutTemplate", back_populates="template_exercises")
    exercise = relationship("Exercise")

class Challenge(Base):
    __tablename__ = "challenges"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    start_date = Column(Date)
    end_date = Column(Date)
    color = Column(String, default="from-orange-500 to-red-500")
    participants_count = Column(Integer, default=0)

class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    likes = Column(Integer, default=0)

    author = relationship("User")



class DashboardWidget(Base):
    __tablename__ = "dashboard_widgets"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String)
    metric = Column(String)
    group_by = Column(String)
    time_range = Column(String)
    chart_type = Column(String, default="area") # area, line, radar, bar
    filter_type = Column(String, default="none")
    filter_id = Column(String, nullable=True) # ID of muscle or exercise (stored as string for flexibility/simplicity or int)
    order = Column(Integer, default=0)

    owner = relationship("User")
