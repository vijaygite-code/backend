from sqlalchemy.orm import Session
from fitness_app.database import SessionLocal, engine
from fitness_app import crud, schemas, models
from fitness_app.seed import SEED_DATA

def verify_and_seed():
    db = SessionLocal()
    try:
        print("Verifying and seeding master data...")
        
        # 1. Muscle Groups
        muscle_group_map = {}
        for mg_name in SEED_DATA.keys():
            db_mg = crud.get_muscle_group_by_name(db, name=mg_name)
            if not db_mg:
                print(f"Creating muscle group: {mg_name}")
                db_mg = crud.create_muscle_group(db, muscle_group=schemas.MuscleGroupCreate(name=mg_name))
            else:
                print(f"Muscle group exists: {mg_name}")
            muscle_group_map[mg_name] = db_mg.id

        # 2. Exercises
        for mg_name, exercise_list in SEED_DATA.items():
            mg_id = muscle_group_map[mg_name]
            for ex_name in exercise_list:
                db_ex = crud.get_exercise_by_name(db, name=ex_name)
                if not db_ex:
                    print(f"Creating exercise: {ex_name}")
                    exercise_schema = schemas.ExerciseCreate(name=ex_name, muscle_group_ids=[mg_id])
                    crud.create_exercise(db, exercise=exercise_schema, user_id=None)
                else:
                    # Check if linked
                    linked_ids = [mg.id for mg in db_ex.muscle_groups]
                    if mg_id not in linked_ids:
                        print(f"Linking {ex_name} to {mg_name}")
                        db_ex.muscle_groups.append(db.query(models.MuscleGroup).get(mg_id))
                        db.commit()

        print("Verification and seeding complete.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    verify_and_seed()
