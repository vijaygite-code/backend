import logging
import os
from sqlalchemy.orm import Session
from fitness_app.core.database import SessionLocal, engine
from fitness_app import models
from fitness_app.auth import auth

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    logger.info("Creating tables...")
    models.Base.metadata.create_all(bind=engine)
    logger.info("Tables created.")

def seed_users(db: Session):
    # Check if admin exists
    admin_email = "admin@gym.com"
    existing_admin = db.query(models.User).filter(models.User.email == admin_email).first()
    
    if not existing_admin:
        logger.info(f"Creating admin user: {admin_email}")
        hashed_password = auth.get_password_hash("admin123")
        admin_user = models.User(
            email=admin_email,
            hashed_password=hashed_password,
            role=models.UserRole.ADMIN,
            age=30,
            weight=75.0,
            height=180.0,
            goals="Manage the gym"
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        logger.info("Admin user created.")
    else:
        logger.info("Admin user already exists.")

    # Check if trainer exists
    trainer_email = "trainer@gym.com"
    existing_trainer = db.query(models.User).filter(models.User.email == trainer_email).first()
    
    if not existing_trainer:
        logger.info(f"Creating trainer user: {trainer_email}")
        hashed_password = auth.get_password_hash("trainer123")
        trainer_user = models.User(
            email=trainer_email,
            hashed_password=hashed_password,
            role=models.UserRole.TRAINER,
            age=28,
            weight=80.0,
            height=185.0,
            goals="Train others"
        )
        db.add(trainer_user)
        db.commit()
        logger.info("Trainer user created.")
    else:
        logger.info("Trainer user already exists.")

    # Create Paid User
    paid_email = "paid@gym.com"
    existing_paid = db.query(models.User).filter(models.User.email == paid_email).first()
    if not existing_paid:
        logger.info(f"Creating paid user: {paid_email}")
        hashed_password = auth.get_password_hash("paid123")
        paid_user = models.User(
            email=paid_email,
            hashed_password=hashed_password,
            role=models.UserRole.PAID,
            age=35,
            weight=70.0,
            height=175.0,
            goals="Get shredded"
        )
        db.add(paid_user)
        db.commit()
        db.refresh(paid_user)
        
        # Add dummy data
        logger.info("Adding dummy data for paid user...")
        # Habit
        db.add(models.Habit(owner_id=paid_user.id, sleep_hours=8, water_liters=3, steps=12000, daily_notes="Great sleep"))
        # Meal
        db.add(models.MealLog(owner_id=paid_user.id, meal_type="Breakfast", description="Oatmeal and Whey", calories=400, protein_g=30, carbs_g=50, fats_g=5))
        # Workout
        workout = models.WorkoutLog(owner_id=paid_user.id, name="Chest Day", notes="Heavy lifting")
        db.add(workout)
        db.commit()
        db.refresh(workout)
        
        # Exercises (ensure they exist first, or creaet on fly? better to use existing master data if any, but we might be empty. Create some exercises first)
        # We need exercises.
        
    # Create Unpaid User (Test User)
    unpaid_email = "test@gym.com"
    existing_unpaid = db.query(models.User).filter(models.User.email == unpaid_email).first()
    if not existing_unpaid:
        logger.info(f"Creating unpaid user: {unpaid_email}")
        hashed_password = auth.get_password_hash("user123")
        unpaid_user = models.User(
            email=unpaid_email,
            hashed_password=hashed_password,
            role=models.UserRole.unpaid,
            age=25,
            weight=65.0,
            height=170.0,
            goals="General Fitness"
        )
        db.add(unpaid_user)
        db.commit()
        logger.info("Unpaid user created.")

def seed_master_data(db: Session):
    # Muscle Groups
    groups = ["Chest", "Back", "Legs", "Shoulders", "Arms", "Core"]
    for g in groups:
        if not db.query(models.MuscleGroup).filter(models.MuscleGroup.name == g).first():
             db.add(models.MuscleGroup(name=g))
    db.commit()
    
    # Helper to get muscle group
    def get_mg(name):
        return db.query(models.MuscleGroup).filter(models.MuscleGroup.name == name).first()

    # Exercises
    # Dictionary of Name -> [Muscle Groups]
    exercises_data = {
        "Bench Press": ["Chest", "Triceps"],
        "Incline Dumbbell Press": ["Chest", "Triceps"],
        "Cable Flys": ["Chest"],
        "Pull Up": ["Back", "Biceps"],
        "Barbell Row": ["Back", "Biceps"],
        "Lat Pulldown": ["Back", "Biceps"],
        "Squat": ["Legs"],
        "Leg Press": ["Legs"],
        "Romanian Deadlift": ["Legs", "Back"],
        "Calf Raises": ["Legs"],
        "Overhead Press": ["Shoulders", "Triceps"],
        "Lateral Raises": ["Shoulders"],
        "Bicep Curl": ["Arms", "Biceps"],
        "Tricep Extension": ["Arms", "Triceps"],
        "Plank": ["Core"],
        "Crunch": ["Core"]
    }

    for name, mgs in exercises_data.items():
        if not db.query(models.Exercise).filter(models.Exercise.name == name).first():
            ex = models.Exercise(name=name, description=f"Standard {name}")
            for mg_name in mgs:
                mg = get_mg(mg_name)
                if mg:
                    ex.muscle_groups.append(mg) # Append works if properly set up, else might need association manually if secondary
                    # SQLAlchemy `secondary` handles append if relationship is defined.
                    pass
            db.add(ex)
    db.commit()

def seed_templates(db: Session):
    if db.query(models.WorkoutTemplate).first():
        logger.info("Templates already exist.")
        return

    logger.info("Seeding workout templates...")
    
    # Helper to get exercise
    def get_ex(name):
        return db.query(models.Exercise).filter(models.Exercise.name == name).first()

    templates = [
        {
            "name": "Push Day",
            "description": "Chest, Shoulders, and Triceps focus",
            "color": "from-blue-500 to-cyan-400",
            "exercises": [("Bench Press", 3, 10), ("Overhead Press", 3, 12), ("Incline Dumbbell Press", 3, 10), ("Lateral Raises", 3, 15), ("Tricep Extension", 3, 12)]
        },
        {
            "name": "Pull Day",
            "description": "Back and Biceps focus",
            "color": "from-purple-500 to-pink-500",
            "exercises": [("Pull Up", 3, 8), ("Barbell Row", 3, 10), ("Lat Pulldown", 3, 12), ("Bicep Curl", 3, 12)]
        },
        {
            "name": "Leg Day",
            "description": "Quads, Hamstrings, and Calves",
            "color": "from-amber-500 to-orange-500",
            "exercises": [("Squat", 4, 8), ("Leg Press", 3, 12), ("Romanian Deadlift", 3, 10), ("Calf Raises", 4, 15)]
        },
        {
            "name": "Full Body",
            "description": "Compound movements for total body",
            "color": "from-emerald-500 to-teal-500",
            "exercises": [("Squat", 3, 8), ("Bench Press", 3, 8), ("Barbell Row", 3, 10), ("Overhead Press", 3, 10)]
        }
    ]

    for t_data in templates:
        template = models.WorkoutTemplate(name=t_data["name"], description=t_data["description"], color=t_data["color"])
        db.add(template)
        db.flush() # get ID

        for ex_name, sets, reps in t_data["exercises"]:
            ex = get_ex(ex_name)
            if ex:
                tex = models.TemplateExercise(template_id=template.id, exercise_id=ex.id, sets=sets, reps=reps)
                db.add(tex)
    
    db.commit()
    logger.info("Templates seeded.")

def reset_db():
    logger.warning("Dropping all tables...")
    models.Base.metadata.drop_all(bind=engine)
    logger.info("All tables dropped.")

def main():
    # reset_db() # DANGER: Only uncomment if you want to wipe data!
    init_db()
    db = SessionLocal()
    try:
        seed_master_data(db)
        seed_users(db)
        seed_templates(db)
    finally:
        db.close()

if __name__ == "__main__":
    main()
