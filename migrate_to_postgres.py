import os
from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy import insert, select, table

def migrate_data():
    sqlite_url = "sqlite:///instance/cinescope.db"
    postgres_url = "postgresql://postgres.wzndeiubajsavvuicfoh:CineScopeSecureDbPass2026!@aws-0-us-east-1.pooler.supabase.com:6543/postgres"

    print("Connecting to SQLite...")
    sqlite_engine = create_engine(sqlite_url)

    print("Connecting to PostgreSQL...")
    pg_engine = create_engine(postgres_url)

    sqlite_meta = MetaData()
    sqlite_meta.reflect(bind=sqlite_engine)

    pg_meta = MetaData()
    pg_meta.reflect(bind=pg_engine)

    # Tables to migrate in order (to respect foreign keys if any)
    tables_to_migrate = [
        'users',
        'followers',
        'watchlists',
        'watched',
        'custom_lists',
        'custom_list_movies',
        'user_favorites'
        # skip api_caches as it's just a cache and can be very large
    ]

    for table_name in tables_to_migrate:
        if table_name not in sqlite_meta.tables:
            print(f"Skipping {table_name} - not found in SQLite")
            continue
        
        sqlite_table = sqlite_meta.tables[table_name]
        pg_table = pg_meta.tables.get(table_name)
        
        if pg_table is None:
            print(f"Skipping {table_name} - not found in Postgres")
            continue
            
        print(f"Migrating {table_name}...")
        
        with sqlite_engine.connect() as sqlite_conn:
            # Read all rows from SQLite
            result = sqlite_conn.execute(select(sqlite_table))
            rows = result.fetchall()
            
            print(f"Found {len(rows)} rows to migrate.")
            
            if not rows:
                continue
                
            # Convert rows to dicts using _mapping for SQLAlchemy 2.0
            records = [dict(row._mapping) for row in rows]
            
            with pg_engine.connect() as pg_conn:
                # Disable foreign key checks for PostgreSQL to simplify bulk inserts temporarily if needed, but ordered list should be fine
                pg_conn.execute(insert(pg_table), records)
                pg_conn.commit()
                print(f"Successfully inserted {len(records)} rows into {table_name}.")

    print("Migration complete!")

if __name__ == "__main__":
    migrate_data()
