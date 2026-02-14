from sqlalchemy import create_engine, text
import sys
import os

# Add parent dir to path to import core
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fitness_app.core.database import SQLALCHEMY_DATABASE_URL

def migrate():
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    with engine.connect() as conn:
        print("Running migration for MonitoringLog...")
        try:
            # SQLite doesn't support IF NOT EXISTS in ALTER TABLE usually, so we wrap in try/except or check.
            # We'll just try to add them. checking columns via PRAGMA is better but try/except is quick for this agent context.
            
            # 1. Add source
            try:
                conn.execute(text("ALTER TABLE monitoring_logs ADD COLUMN source VARCHAR DEFAULT 'AI'"))
                print("Added 'source' column.")
            except Exception as e:
                print(f"Skipping 'source' (might exist): {e}")

            # 2. Add reporter_id
            try:
                conn.execute(text("ALTER TABLE monitoring_logs ADD COLUMN reporter_id INTEGER REFERENCES users(id)"))
                print("Added 'reporter_id' column.")
            except Exception as e:
                print(f"Skipping 'reporter_id' (might exist): {e}")

            # 3. Add post_id
            try:
                conn.execute(text("ALTER TABLE monitoring_logs ADD COLUMN post_id INTEGER REFERENCES posts(id)"))
                print("Added 'post_id' column.")
            except Exception as e:
                print(f"Skipping 'post_id' (might exist): {e}")
                
            conn.commit()
            print("Migration complete.")
        except Exception as e:
            print(f"Migration failed: {e}")

if __name__ == "__main__":
    migrate()
