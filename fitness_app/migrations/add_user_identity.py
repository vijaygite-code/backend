import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load env variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL not set in .env")

print(f"Connecting to: {DATABASE_URL}")
engine = create_engine(DATABASE_URL)

def run_migration():
    # Use engine.begin() for transaction management
    with engine.begin() as connection:
        print("Starting migration...")
        
        try:
            # Postgres specific: Add column if not exists
            # Ideally we check information_schema, but simple try/except valid in migration scripts too
            
            print("Adding username column...")
            connection.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS username VARCHAR"))
            # Unique constraint
            connection.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ix_users_username ON users (username)"))
            print("username column added/verified.")

            print("Adding full_name column...")
            connection.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS full_name VARCHAR"))
            print("full_name column added/verified.")
            
        except Exception as e:
            print(f"Migration error: {e}")
            raise e

if __name__ == "__main__":
    run_migration()


# Load env variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL not set in .env")

print(f"Connecting to: {DATABASE_URL}")
engine = create_engine(DATABASE_URL)

def run_migration():
    with engine.connect() as connection:
        # Check if columns exist
        print("Checking if columns exist...")
        
        # This is a bit hacky for "enterprise" but works for simple migrations without Alembic
        # for SQLite/Postgres compatibility we use standard SQL or specific checks.
        # Let's just try to ADD them and catch errors if they exist, or check explicitly.
        
        # SQLite doesn't support IF NOT EXISTS in ALTER TABLE mostly.
        # Postgres does.
        
        try:
            # 1. Add username
            print("Adding username column...")
            connection.execute(text("ALTER TABLE users ADD COLUMN username VARCHAR"))
            # Add Unique constraint? SQLite requires recreating table for constraints usually if strict.
            # But we can try creating unique index.
            connection.execute(text("CREATE UNIQUE INDEX ix_users_username ON users (username)"))
            print("username column added.")
        except Exception as e:
            print(f"Skipping username add (might exist): {e}")

        try:
            # 2. Add full_name
            print("Adding full_name column...")
            connection.execute(text("ALTER TABLE users ADD COLUMN full_name VARCHAR"))
            print("full_name column added.")
        except Exception as e:
            print(f"Skipping full_name add (might exist): {e}")
            
        # Commit not needed with autocommit engine or implicit commit in some drivers, 
        # but let's be safe if transaction is active. 
        # SQLAlchemy 1.4+ with future=True or 2.0 requires explicit commit
        try:
            connection.commit()
        except:
            pass # Transaction might not be active

if __name__ == "__main__":
    run_migration()
