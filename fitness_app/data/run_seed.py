import logging
from fitness_app.database import SessionLocal
from fitness_app.seed import seed_database

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting manual database seeding...")
    db = SessionLocal()
    try:
        seed_database(db)
        logger.info("Manual database seeding completed successfully.")
    except Exception as e:
        logger.error(f"An error occurred during seeding: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
