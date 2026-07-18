"""
One-time migration: adds the `marks` JSON column to the users table.
Run once: py -3.11 migrate_add_marks.py
"""
from sqlalchemy import text
from database import engine

with engine.connect() as conn:
    conn.execute(text("""
        ALTER TABLE users
        ADD COLUMN IF NOT EXISTS marks JSONB DEFAULT '[]'::jsonb;
    """))
    conn.commit()
    print("✅ Migration complete: 'marks' column added to users table.")
