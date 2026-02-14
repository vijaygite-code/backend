from sqlalchemy.orm import Session
from . import crud, schemas, models # Import the models module

# The new, comprehensive list of master data
SEED_DATA = {
    "Chest (Pectoralis Major)": [
        "Barbell Bench Press", "Dumbbell Bench Press", "Push-Ups", "Incline Bench Press",
        "Decline Bench Press", "Chest Fly (Dumbbell or Cable)", "Dips (Chest Emphasis)"
    ],
    "Back (Lats, Rhomboids, Traps)": [
        "Pull-Ups", "Chin-Ups", "Lat Pulldown", "Bent-Over Row (Barbell or Dumbbell)",
        "Seated Cable Row", "T-Bar Row", "Deadlift", "Single-Arm Dumbbell Row",
        "Face Pull", "Straight-Arm Pulldown"
    ],
    "Shoulders (Deltoids)": [
        "Overhead Press (Barbell or Dumbbell)", "Arnold Press", "Lateral Raise",
        "Front Raise", "Rear Delt Fly", "Upright Row", "Shoulder Press Machine"
    ],
    "Biceps": [
        "Barbell Curl", "Dumbbell Curl", "Hammer Curl", "Preacher Curl",
        "Concentration Curl", "Incline Dumbbell Curl", "Chin-Up (Biceps Emphasis)"
    ],
    "Triceps": [
        "Triceps Dip", "Close-Grip Bench Press", "Triceps Pushdown (Cable)",
        "Overhead Dumbbell Extension", "Skullcrusher", "Kickback", "Bench Dip"
    ],
    "Quadriceps": [
        "Barbell Back Squat", "Front Squat", "Leg Press", "Bulgarian Split Squat",
        "Walking Lunge", "Step-Up", "Leg Extension"
    ],
    "Hamstrings": [
        "Romanian Deadlift (RDL)", "Lying Leg Curl", "Seated Leg Curl",
        "Good Morning", "Nordic Hamstring Curl", "Glute-Ham Raise"
    ],
    "Glutes": [
        "Hip Thrust", "Glute Bridge", "Barbell Squat", "Deadlift",
        "Cable Kickback", "Step-Up", "Bulgarian Split Squat"
    ],
    "Calves": [
        "Standing Calf Raise", "Seated Calf Raise", "Donkey Calf Raise",
        "Box Jump", "Jump Rope", "Farmer’s Walk (on toes)"
    ],
    "Abs (Rectus Abdominis)": [
        "Crunch", "Hanging Leg Raise", "Cable Crunch", "Ab Rollout (Wheel or Barbell)",
        "Plank", "Reverse Crunch"
    ],
    "Obliques": [
        "Russian Twist", "Side Plank", "Bicycle Crunch", "Woodchopper (Cable or Dumbbell)",
        "Oblique Crunch", "Landmine Rotation"
    ],
    "Lower Back (Erector Spinae)": [
        "Deadlift", "Back Extension (Hyperextension)", "Superman Hold",
        "Bird Dog", "Good Morning", "Rack Pull"
    ],
    "Forearms": [
        "Wrist Curl", "Reverse Wrist Curl", "Farmer’s Carry", "Towel Pull-Up",
        "Plate Pinch Hold", "Dead Hang"
    ]
}

def seed_database(db: Session):
    print("Seeding database with comprehensive exercise list...")
    muscle_group_map = {}
    
    # Create all muscle groups first
    for mg_name in SEED_DATA.keys():
        db_mg = crud.get_muscle_group_by_name(db, name=mg_name)
        if not db_mg:
            db_mg = crud.create_muscle_group(db, muscle_group=schemas.MuscleGroupCreate(name=mg_name))
            print(f"Created muscle group: {mg_name}")
        muscle_group_map[mg_name] = db_mg.id

    # Create exercises and link them to the appropriate muscle group
    for mg_name, exercise_list in SEED_DATA.items():
        mg_id = muscle_group_map[mg_name]
        for ex_name in exercise_list:
            db_ex = crud.get_exercise_by_name(db, name=ex_name)
            if not db_ex:
                exercise_schema = schemas.ExerciseCreate(name=ex_name, muscle_group_ids=[mg_id])
                crud.create_exercise(db, exercise=exercise_schema, user_id=None)
                print(f"Created exercise: {ex_name} for {mg_name}")
            # If exercise exists, ensure it's linked to the current muscle group
            elif mg_id not in [mg.id for mg in db_ex.muscle_groups]:
                db_ex.muscle_groups.append(db.query(models.MuscleGroup).get(mg_id))
                db.commit()
                print(f"Linked existing exercise '{ex_name}' to '{mg_name}'")

    print("Database seeding complete.")
