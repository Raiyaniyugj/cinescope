import os
from sqlalchemy import create_engine, text

def migrate_google_id():
    postgres_url = "postgresql://postgres.wzndeiubajsavvuicfoh:CineScopeSecureDbPass2026!@aws-0-us-east-1.pooler.supabase.com:6543/postgres"

    print("Connecting to PostgreSQL...")
    pg_engine = create_engine(postgres_url)

    with pg_engine.connect() as conn:
        try:
            print("Altering users table: drop not null constraint on password_hash")
            conn.execute(text("ALTER TABLE users ALTER COLUMN password_hash DROP NOT NULL;"))
        except Exception as e:
            print(f"Error or already altered: {e}")
            
        try:
            print("Altering users table: add google_id column")
            conn.execute(text("ALTER TABLE users ADD COLUMN google_id VARCHAR(100) UNIQUE;"))
        except Exception as e:
            print(f"Error or already added: {e}")
            
        conn.commit()

    print("Migration complete!")

if __name__ == "__main__":
    migrate_google_id()
